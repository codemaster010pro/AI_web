from langgraph_tools import all_tools
from schema import tutor
from langchain_core.messages import ToolMessage



async def tool_node(state:tutor):
    tools_by_name = {tool.name: tool for tool in all_tools}
    messages = state.get("response") or state.get("messages")
    
    if not messages:
        return {"messages": []}
    
    last_message = messages[-1]
    tool_results = []
    
    tool_call = getattr(last_message, "tool_calls", [])
    for tool in tool_call:
        
        tool_name = tool.get("name")
        tool_args = tool.get("args")
        tool_id = tool.get("id")
        
        called_tool = tools_by_name.get(tool_name)
        
        if called_tool:
            result = await called_tool.ainvoke(tool_args)
            
            tool_results.append(ToolMessage(
                content=str(result),
                name=tool_name,
                tool_call_id=tool_id
            ))
        
    return {"messages": tool_results}

def conditional_node(state:tutor):
    last_response = state.get("response") or state.get("messages", [])
    
    if not last_response:
        return "end"
    
    last = last_response[-1]
    
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tool_node"
    
    return "end"