from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from langgraph.graph import StateGraph,END,START

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3)

class engine(BaseModel):
    uid:int
    interested_subjects:str
    response:str = ""
    
def quiz(state:engine):
    current_uid = state.uid
    current_interested_subjects = state.interested_subjects
    
    core_prompt = SystemMessage(
        content=(
            "You are an expert AI Diagnostic Tutor for an adaptive learning platform. "
            "Your goal is to evaluate a student's learning patterns, personality, and preferences. "
            "\n\nRules:\n"
            "1. Ask 4 to 6 targeted, short questions to determine if the user prefers "
            "visual diagrams, hands-on code, deep-dive theory, or quick high-yield summaries.\n"
            "2. Keep your tone encouraging, direct, and conversational.\n"
            "3. Ask 1 questions at a time so the user isn't overwhelmed.\n"
            "4. Focus on practical scenarios rather than abstract psychological terms."
        )
    )
    
    user_reply = HumanMessage(
        content=f"Student ID: {current_uid}. Current course/subject interest: {current_interested_subjects}. Begin the diagnostic evaluation."
    )
    
    response = llm.invoke([core_prompt,user_reply])
    return{"response":response.content}

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
