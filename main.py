from langchain_groq import ChatGroq
import operator
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,END,START
from langgraph_tools import all_tools

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.)

llm_with_tools = llm.bind_tools(all_tools)

class engine(TypedDict):
    uid:int
    interested_subjects:str
    response:Annotated[list[BaseMessage], operator.add]
    
    
    
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
            ("human", "Student ID: {uid}. Current course/subject interest: {interested_subjects}. Begin the diagnostic evaluation.")
        ]) 
    
    chain = prompt | llm_with_tools  
    
    ai_response = chain.invoke({
        "uid": state["uid"],
        "interested_subjects": state["interested_subjects"]
    })

    return {"response": [ai_response]}

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
