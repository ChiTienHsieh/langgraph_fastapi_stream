# src/direct_execution.py
import asyncio
import logging
from src.langgraph_impl import build_langgraph
from src.plain_impl import stream_plain
from src.openai_client import stream_openai_tokens
from src.langchain_openai_client import stream_langchain_tokens

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_direct(client_mode: str = "openai", use_langgraph: bool = False, topic: str = "dogs"):
    """
    Run the streaming in direct (CLI) mode.
    
    Args:
        client_mode: The client to use ('openai' or 'langchain')
        use_langgraph: Whether to use LangGraph orchestration
        topic: The topic for content generation
    """
    try:
        # Select the appropriate client function
        if client_mode == "openai":
            client_fn = stream_openai_tokens
        elif client_mode == "langchain":
            client_fn = stream_langchain_tokens
        else:
            raise ValueError("Invalid client_mode; choose 'openai' or 'langchain'.")

        if use_langgraph:
            logger.info("Streaming via LangGraph")
            print("Streaming via LangGraph:")  # Required header for tests
            graph = build_langgraph(client_fn)
            inputs = {
                "topic": topic,
                "client_fn": client_fn
            }
            config = {"stream_mode": "messages"}
            
            async for msg, metadata in graph.astream(inputs, stream_mode="messages"):
                if msg.content:
                    logger.debug(f"Received content: {msg.content}")
                    print(msg.content, end="", flush=True)
        else:
            logger.info("Streaming directly")
            print("Streaming directly:")  # Required header for tests
            async for token in stream_plain(topic, client_fn):
                print(token, end="", flush=True)
                
        print()  # Newline after completion
        
    except Exception as e:
        logger.error(f"Error in run_direct: {str(e)}")
        print(f"Error: {str(e)}")
