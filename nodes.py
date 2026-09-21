from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from model import llm
from schema import engine,evaluation,tutor
from sqlite import save_to_db,fetch_userdata
from langgraph_tools import all_tools

llm_with_tools = llm.bind_tools(all_tools)    
evaluation_llm = llm.with_structured_output(evaluation, method="json_mode")
    
def extract_text(msg):
    if hasattr(msg, "content"):
        return msg.content
    elif isinstance(msg, (list, tuple)) and len(msg) > 1:
        return msg[1]
    return str(msg)

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
                "5. dont use any tools or json format"
                "6. Do NOT include learning profiles, recaps, summary tables, or progress reflections.\n"
            )),
            MessagesPlaceholder(variable_name="response")
        ]) 
    
    quiz_llm = llm.bind(tool_choice = "none")
    chain = prompt | quiz_llm
    ai_response = chain.invoke({
        "response": state["response"],
        "question_number": state.get("no_of_questions", 0) + 1
    })

    return {"response": [ai_response],
            "no_of_questions": state.get("no_of_questions", 0) + 1}

def evaluate(state: engine):
    if len(state["response"]) < 2:
        return {"evaluation_of_user": []}
    
    last_user_input = extract_text(state["response"][-1])
    last_ai_question = extract_text(state["response"][-2])  
    
    evaluation_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an evaluation engine. Respond strictly in valid JSON format matching the schema.\n"
     "CRITICAL: You MUST include all schema fields (`score`, `feedback`, `option_selected`, `learning_preference`, `insights`). "
     "If a field does not apply, provide a default string like 'N/A' or 'None'."),
    ("human", "Question: {question}\nUser Answer: {answer}")
])
    
    evaluation_chain = evaluation_prompt | evaluation_llm
    analysis_result : evaluation = evaluation_chain.invoke({
        "question": last_ai_question,
        "answer": last_user_input
    })
    
    latest_entry = analysis_result.model_dump()
    return {"evaluation_of_user": [latest_entry]}

def quiz_stop(state: engine):
    
    if state.get("no_of_questions", 0) >= 7:
        evaluation = state.get("evaluation_of_user", [])
        
        learning_preference = [item.get("learning_preference") for item in evaluation if "learning_preference" in item]
        dominant_preference = max(set(learning_preference), key=learning_preference.count) if learning_preference else "General"
        
        save_to_db(uid=state["uid"], interested_subjects=state["interested_subjects"], learning_preference=dominant_preference, evaluation=evaluation)
        return "end"
    return "quiz"

def tutor_node(state:tutor):
    uid = state["uid"]
    user_profile = fetch_userdata(uid)
    
    if user_profile:
        learning_preference = user_profile["learning_preference"]
        interested_subjects = user_profile["interested_subjects"]
    else:
        learning_preference = "General"
        interested_subjects = "General topics"
        
    system_prompt = f"""
            You are an expert personalized AI Tutor specializing in {interested_subjects}.
            The student's primary learning style is: {learning_preference}.
            
            Adapt your explanations according to their style:
            - If 'Hands-on Code': Focus heavily on practical, executable code snippets and examples.
            - If 'Visual': Use structured diagrams, ASCII flowcharts, and vivid conceptual analogies.
            - If 'Deep Theory': Provide underlying mechanics, architectural context, and formal explanations.
            - If 'Quick Summary': Give high-yield bullet points and concise explanations.
            """
            
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history")
        ])
            
    chain = prompt | llm_with_tools
    response = chain.invoke({
        "chat_history": state["messages"]
    })
            
    return {"messages": [response]}