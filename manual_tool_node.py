from langgraph_tools import all_tools
from schema import engine
from langchain_core.messages import ToolMessage



async def tool_node(state:engine):
    tools_by_name = {tool.name: tool for tool in all_tools}
    messages = state.get("response") or state.get("messages") or []
    
    if not messages:
        return {"messages": []}
    
    last_message = messages[-1]
    tool_results = []
    
    tool_call = getattr(last_message, "tool_calls", [])
    for tool in tool_call:
        
        tool_name = tool.get("name")
        tool_args = tool.get("args")
        tool_id = tool.get("id")
        
        if isinstance(tool_args, dict):
            if "args" in tool_args:
                nested = tool_args["args"]
                if isinstance(nested, list) and len(nested) > 0 and isinstance(nested[0], dict):
                    tool_args = nested[0]
                elif isinstance(nested, dict):
                    tool_args = nested
            
            for k, v in list(tool_args.items()):
                if isinstance(v, dict) and k != "args":
                    if any(param in v for param in ["query", "search_query", "url", "youtube_url"]):
                        tool_args = v
                        break
        
        called_tool = tools_by_name.get(tool_name)
        
        if called_tool:
            try:
                result = await called_tool.invoke(tool_args)
            except Exception as e:
                result = f"Error {tool_name}: {str(e)}"
                
            tool_results.append(ToolMessage(
                content=str(result),
                name=tool_name,
                tool_call_id=tool_id
            ))
        
    return {"messages": tool_results}

def conditional_node(state:engine):
    last_response = state.get("response") or state.get("messages", []) or []
    
    if not last_response:
        return "end"
    
    last = last_response[-1]
    
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tool_node"
    
    return "end"