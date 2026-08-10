from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage , AIMessage
from pydantic import BaseModel,Field
from langgraph.graph import StateGraph,END,START

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.)

class engine(BaseModel):
    uid:int
    interested_subjects:str
    response:list = Field(default_factory=list)
#   user_preference = str
#   user_history = str
    
    
    
def quiz(state:engine):
    current_uid = state.uid
    current_interested_subjects = state.interested_subjects
    current_reponse_list = state.response
#   current_user_preference = state.user_preference
#   current_user_history = state.user_history
    
    core_prompt = SystemMessage(
        content=(
            "You are an expert AI Diagnostic Tutor for an adaptive learning platform. "
            "Your goal is to evaluate a student's learning patterns, personality, and preferences.\n\n"
            "Rules:\n"
            "1. Evaluate if the student prefers visual diagrams, hands-on code, deep-dive theory, or quick high-yield summaries.\n"
            "2. Keep your tone encouraging, direct, and conversational.\n"
            "3. Ask 1 question at a time with 4 distinct multiple-choice options.\n"
            "4. Focus on practical learning scenarios rather than abstract psychology terms."
        )
    )
    
    user_reply = HumanMessage(
        content = f"Student ID: {current_uid}. Current course/subject interest: {current_interested_subjects}. Begin the diagnostic evaluation."
    )
    
    response_text = llm.invoke([core_prompt,user_reply]).content
    ai_messages = AIMessage(response_text)
    updated_list = current_reponse_list + [ai_messages]
    return {"response":updated_list}

graph = StateGraph(engine)

graph.add_node("quiz",quiz)
graph.add_edge(START,"quiz")
graph.add_edge("quiz",END)

quiz_node = graph.compile()

initial_state = {
    "uid": 101,
    "interested_subjects": "LangGraph vs LangChain for building multi-agent systems"
}

result = quiz_node.invoke(initial_state)
print(result)
