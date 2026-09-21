from langchain.messages import AIMessage, HumanMessage
from schema import engine,tutor
from langgraph.graph import StateGraph,END,START
from nodes import quiz,evaluate,quiz_stop,tutor_node
from manual_tool_node import tool_node,conditional_node
from langgraph.checkpoint.memory import MemorySaver 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlite import save_to_db,fetch_userdata

app = FastAPI(title = "AI adaptive learning Web App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
memory = MemorySaver()
#======quiz_graph======
graph = StateGraph(engine)

graph.add_node("quiz",quiz)
graph.add_node("evaluate",evaluate)

graph.add_edge(START,"evaluate")
graph.add_edge("evaluate","quiz")
graph.add_conditional_edges("quiz",quiz_stop, {
    "quiz": END,
    "end": END
    
})

quiz_graph = graph.compile(checkpointer=memory)

#======tutor_graph======

Tutor_graph = StateGraph(tutor)

Tutor_graph.add_node("tutor_node",tutor_node)
Tutor_graph.add_node("tool_node",tool_node)

Tutor_graph.add_edge(START,"tutor_node")
Tutor_graph.add_conditional_edges("tutor_node",conditional_node, {
    "tool_node": "tool_node",
    "tutor_node": "tutor_node",
    "end": END
})
Tutor_graph.add_edge("tool_node","tutor_node")

tutor_graph = Tutor_graph.compile(checkpointer=memory)


#===========web app=========
    
class quizReq(BaseModel):
    uid:int
    interested_subjects:str
    user_answer:str
    
class chatReq(BaseModel):
    uid:int
    message:str
    
@app.post("/quiz/next")
async def run_quiz(req:quizReq):
    config = {"configurable":{"thread_id" : f"quiz_{req.uid}"}}
    
    state_input = {
        "uid": req.uid,
        "interested_subjects": req.interested_subjects,
        "response": [("user", req.user_answer)]
    }
    
    output = await quiz_graph.ainvoke(state_input, config=config)
    
    no_of_questions = output.get("no_of_questions", 0)
    is_end = no_of_questions >= 7
    
    last_msg = output["response"][-1]
    ai_text = last_msg.content if hasattr(last_msg, "content") else last_msg[1]
    
    return {
        "status": "completed" if is_end else "in_progress",
        "question_number": no_of_questions,
        "ai_response": ai_text,
    }
    
@app.post("/tutor/chat")
async def run_tutor(req:chatReq):
   try:
        config = {"configurable":{"thread_id" : f"tutor_{req.uid}"}}
        
        output = await tutor_graph.ainvoke({
            "uid": req.uid,
            "messages": [HumanMessage(content=req.message)]
        }, config=config)
        
        message_history = output.get("messages") or output.get("response") or []
        
        ai_reply = "No response yet."
        for msg in reversed(message_history):
            if isinstance(msg,AIMessage) and msg.content:
                ai_reply = msg.content
                break
        
        return {
            "reply": ai_reply
        }
        
   except Exception as e:
       print(e)
       raise e
    