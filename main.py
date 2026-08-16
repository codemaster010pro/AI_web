from schema import engine
from langgraph.graph import StateGraph,END,START
from nodes import quiz,evaluate,quiz_stop

graph = StateGraph(engine)

graph.add_node("quiz",quiz)
graph.add_node("evaluate",evaluate)

graph.add_edge(START,"quiz")
graph.add_edge("quiz","evaluate")
graph.add_conditional_edges("evaluate",quiz_stop, {
    "quiz": "quiz",
    "end": END
    
})

app = graph.compile()

    

       

