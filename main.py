from schema import engine,tutor
from langgraph.graph import StateGraph,END,START
from nodes import quiz,evaluate,quiz_stop,tutor_node
from manual_tool_node import tool_node,conditional_node
from langgraph.checkpoint.memory import MemorySaver 

memory = MemorySaver()
#======quiz_graph======
graph = StateGraph(engine)

graph.add_node("quiz",quiz)
graph.add_node("evaluate",evaluate)

graph.add_edge(START,"quiz")
graph.add_edge("quiz","evaluate")
graph.add_conditional_edges("evaluate",quiz_stop, {
    "quiz": "quiz",
    "end": END
    
})

quiz_graph = graph.compile(checkpointer=memory)
print(quiz_graph.get_graph().draw_mermaid())
#======tutor_graph======

Tutor_graph = StateGraph(tutor)

Tutor_graph.add_node("tutor",tutor_node)
Tutor_graph.add_node("tool_node",tool_node)

Tutor_graph.add_edge(START,"tutor")
Tutor_graph.add_conditional_edges("tutor",conditional_node, {
    "tool_node": "tool_node",
    "end": END
})
Tutor_graph.add_edge("tool_node","tutor")

tutor_graph = Tutor_graph.compile(checkpointer=memory)
print(tutor_graph.get_graph().draw_mermaid())

    

       

