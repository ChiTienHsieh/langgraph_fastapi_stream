# src/langgraph_impl.py
import asyncio
from langgraph.graph import StateGraph, START, END

async def langgraph_node(state, config):
    """
    A LangGraph node that uses a client function (passed in state) to stream tokens.
    Expects state["client_fn"] to be an async generator function.
    """
    topic = state["topic"]
    client_fn = state["client_fn"]
    async for token in client_fn(topic):
        yield {"token": token}

def build_langgraph(client_fn):
    """
    Constructs a LangGraph state graph using the langgraph_node.
    """
    graph = (
        StateGraph(dict)
        .add_node(langgraph_node)
        .add_edge(START, "langgraph_node")
        .add_edge("langgraph_node", END)
        .compile()
    )
    return graph
