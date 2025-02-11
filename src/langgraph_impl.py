# src/langgraph_impl.py
import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from typing import Dict, Any, AsyncGenerator, Tuple, Optional

class LangGraphError(Exception):
    """Custom exception for LangGraph-related errors."""
    pass

async def langgraph_node(state: Dict[str, Any], config: RunnableConfig) -> AsyncGenerator[Dict[str, Any], None]:
    """
    A LangGraph node that uses a client function (passed in state) to stream tokens.
    Expects state["client_fn"] to be an async generator function.
    
    Args:
        state: The current state containing topic and client function
        config: RunnableConfig for proper streaming in Python < 3.11
    
    Yields:
        Dict[str, Any]: The output containing the token and any error information
    
    Raises:
        LangGraphError: If there are issues with the client function or token streaming
    """
    topic = state.get("topic")
    client_fn = state.get("client_fn")
    
    if not topic or not client_fn:
        raise LangGraphError("Missing required state: 'topic' or 'client_fn'")
    
    try:
        content_received = False
        async for token in client_fn(topic, config=config):
            if not isinstance(token, (str, dict)):
                continue
                
            # Handle both string tokens and dictionary responses
            content = token if isinstance(token, str) else token.get('content', '')
            
            if content and content.strip():
                content_received = True
                # Return in the format expected by LangGraph
                yield {"content": content}
        
        if not content_received:
            yield {"error": "No meaningful content received from LLM"}
            
    except Exception as e:
        error_msg = f"Error during token streaming: {str(e)}"
        yield {"error": error_msg}

def build_langgraph(client_fn):
    """
    Constructs a LangGraph state graph using the langgraph_node.
    
    Args:
        client_fn: An async generator function that streams tokens
        
    Returns:
        A compiled LangGraph workflow
    """
    workflow = StateGraph(dict)
    
    # Add the node and set it as the entry point
    workflow.add_node("generate", langgraph_node)
    workflow.set_entry_point("generate")
    
    # Add edge to END
    workflow.add_edge("generate", END)
    
    # Compile the graph
    return workflow.compile()
