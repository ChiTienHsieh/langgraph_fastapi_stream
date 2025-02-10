# src/langgraph_impl.py
import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig

from typing import Dict, Any, AsyncGenerator, Tuple

async def langgraph_node(state: Dict[str, Any], config: RunnableConfig) -> AsyncGenerator[Dict[str, Any], None]:
    """
    A LangGraph node that uses a client function (passed in state) to stream tokens.
    Expects state["client_fn"] to be an async generator function.
    
    Args:
        state: The current state containing topic and client function
        config: RunnableConfig for proper streaming in Python < 3.11
    
    Yields:
        Dict[str, Any]: The output containing the token
    """
    topic = state["topic"]
    client_fn = state["client_fn"]
    
    async for token in client_fn(topic, config=config):
        # Return in the format expected by LangGraph
        yield {"content": token}

def build_langgraph(client_fn):
    """
    Constructs a LangGraph state graph using the langgraph_node.
    """
    workflow = StateGraph(dict)
    
    # Add the node and set it as the entry point
    workflow.add_node("generate", langgraph_node)
    workflow.set_entry_point("generate")
    
    # Add edge to END
    workflow.add_edge("generate", END)
    
    # Compile the graph
    return workflow.compile()
