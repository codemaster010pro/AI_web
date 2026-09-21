from langgraph_tools import all_tools
from schema import engine
from langchain_core.messages import ToolMessage



async def tool_node(state:engine):
    tools_by_name = {tool.name: tool for tool in all_tools}
    response = state["response"] or state["messages"] or []
    
    if not response:
        return {"response": []}
    
    last_message = response[-1]
    tool_results = []
    
    tool_call = getattr(last_message, "tool_calls", [])
    for tool in tool_call:
        
        tool_name = tool.get("name")
        tool_args = tool.get("args")
        tool_id = tool.get("id")
        
        called_tool = tools_by_name.get(tool_name)
        
        if called_tool:
            result = await called_tool.invoke(tool_args)
            
            tool_results.append(ToolMessage(
                content=str(result),
                name=tool_name,
                tool_call_id=tool_id
            ))
        
    return {"response": tool_results}

def conditional_node(state:engine):
    last_response = state["response"] or []
    
    if not last_response:
        return "tutor_node"
    
    last = last_response[-1]
    
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools_node"
    else:
        return "end"