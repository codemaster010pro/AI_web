from langgraph_tools import all_tools
from schema import engine
from langchain_core.messages import ToolMessage



def tool_node(state:engine):
    tools_by_name = {tool.name: tool for tool in all_tools}
    response = state["response"]
    
    tool_results = []
    
    for tool in response[-1].tool_calls:
        
        tool_name = tool.get("name")
        tool_args = tool.get("args")
        tool_id = tool.get("id")
        
        called_tool = tools_by_name.get(tool_name)
        
        result = called_tool.invoke(tool_args)
        
        tool_results.append(ToolMessage(
            content=str(result),
            name=tool_name,
            tool_call_id=tool_id
        ))
       
    return {"response": tool_results}

def conditional_node(state:engine):
    last_response = state["response"][-1]
    
    if last_response.tool_calls:
        return "tool_node"
    else:
        return "end"