# src/langgraph_impl.py
import logging
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def call_model(state, config: RunnableConfig):
    """
    A LangGraph node that uses a client function to generate content.
    
    Args:
        state: The current state containing topic and client function
        config: RunnableConfig for proper streaming
    
    Returns:
        Dict containing the generated content or error
    """
    topic = state.get("topic")
    client_fn = state.get("client_fn")
    
    if not topic or not client_fn:
        logger.error("Missing required state: 'topic' or 'client_fn'")
        return {"error": "Missing required state: 'topic' or 'client_fn'"}
    
    try:
        logger.info(f"Generating content for topic: {topic}")
        full_response = ""
        async for token in client_fn(topic, config=config):
            if isinstance(token, dict):
                if "error" in token:
                    logger.error(f"Error from client: {token['error']}")
                    return {"error": token["error"]}
                elif "content" in token:
                    logger.debug(f"Received token: {token['content']}")
                    full_response += token["content"]
            elif isinstance(token, str):
                logger.debug(f"Received string token: {token}")
                full_response += token
        
        if not full_response.strip():
            logger.warning("No content received from client")
            return {"error": "No content received"}
            
        logger.info("Successfully generated content")
        return {"joke": full_response}  # Match the working example's response format
            
    except Exception as e:
        error_msg = f"Error in call_model: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

def build_langgraph(client_fn):
    """
    Constructs a LangGraph state graph.
    
    Args:
        client_fn: An async function that generates content
        
    Returns:
        A compiled LangGraph workflow
    """
    workflow = (
        StateGraph(dict)
        .add_node("call_model", call_model)
        .add_edge(START, "call_model")
        .add_edge("call_model", END)
        .compile()
    )
    
    logger.info("Built LangGraph workflow")
    return workflow
