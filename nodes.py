from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from model import llm
from schema import engine,evaluation
from sqlite import save_to_db
    
evaluation_llm = llm.with_structured_output(evaluation)
    
def quiz(state:engine):

    prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert AI Diagnostic Tutor for an adaptive learning platform. "
                "Your goal is to evaluate a student's learning patterns, personality, and preferences.\n"
                "Rules:\n"
                "1. Evaluate if the student prefers visual diagrams, hands-on code, deep-dive theory, or quick high-yield summaries.\n"
                "2. Keep your tone encouraging, direct, and conversational.\n"
                "3. Ask 1 question at a time with 4 distinct multiple-choice options.\n"
                "4. Focus on practical learning scenarios rather than abstract psychology terms."
            )),
            MessagesPlaceholder(variable_name="response")
        ]) 
    
    chain = prompt | llm
    ai_response = chain.invoke({
        "response": state["response"],
        "question_number": state.get("no_of_questions", 0) + 1
    })

    return {"response": [ai_response],
            "no_of_questions": state.get("no_of_questions", 0) + 1}

def evaluate(state: engine):
    last_user_input = state["response"][-1].content
    last_ai_question = state["response"][-2].content
    
    evaluation_prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze the student's answer choice and classify their learning preference."),
        ("human", "Question Asked:\n{question}\n\nStudent Answer:\n{answer}")
    ])
    
    evaluation_chain = evaluation_prompt | evaluation_llm
    analysis_result : evaluation = evaluation_chain.invoke({
        "question": last_ai_question,
        "answer": last_user_input
    })
    
    latest_entry = analysis_result.model_dump()
    return {"evaluation_of_user": [latest_entry]}

def quiz_stop(state: engine):
    if state.get("no_of_questions", 0) >= 6:
        evaluation = state.get("evaluation_of_user", [])
        
        learning_preference = [item.get("learning_preference") for item in evaluation if "learning_preference" in item]
        dominant_preference = max(set(learning_preference), key=learning_preference.count) if learning_preference else "General"
        
        save_to_db(uid=state["uid"], interested_subjects=state["interested_subjects"], learning_preference=dominant_preference, evaluation_list=evaluation)
        return "end"
    return "quiz"