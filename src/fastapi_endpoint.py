# src/fastapi_endpoint.py
import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
from src.langgraph_impl import build_langgraph
from src.plain_impl import stream_plain
from src.openai_client import stream_openai_tokens
from src.langchain_openai_client import stream_langchain_tokens

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(client_mode: str = "openai", use_langgraph: bool = False):
    """Create FastAPI application with streaming endpoint."""
    app = FastAPI()
    
    # Select client function based on flag
    if client_mode == "openai":
        client_fn = stream_openai_tokens
    elif client_mode == "langchain":
        client_fn = stream_langchain_tokens
    else:
        raise ValueError("Invalid client_mode. Use 'openai' or 'langchain'.")

    @app.get("/stream")
    async def stream_joke(topic: str = Query("dogs", description="Topic for the joke")):
        """Endpoint that streams generated content."""
        logger.info(f"Received request for topic: {topic}")
        
        async def event_generator():
            content_received = False
            try:
                if use_langgraph:
                    logger.info("Using LangGraph for streaming")
                    graph = build_langgraph(client_fn)
                    inputs = {
                        "topic": topic,
                        "client_fn": client_fn
                    }
                    config = {"stream_mode": "messages"}
                    
                    async for msg, metadata in graph.astream(inputs, stream_mode="messages"):
                        if msg.content:
                            content_received = True
                            logger.debug(f"Received content: {msg.content}")
                            yield f"{msg.content}\n"
                            await asyncio.sleep(0.3)  # Match the working example's delay
                else:
                    logger.info("Using direct streaming")
                    async for token in stream_plain(topic, client_fn):
                        if isinstance(token, dict):
                            if "error" in token:
                                logger.error(f"Streaming error: {token['error']}")
                                yield f"Error: {token['error']}\n"
                                content_received = True  # Error is still content
                            elif "content" in token:
                                content_received = True
                                yield token["content"]
                        else:
                            content_received = True
                            yield token
                        await asyncio.sleep(0.01)
                
                if not content_received:
                    logger.warning("No content received")
                    yield "No content received from LLM\n"
                    
            except Exception as e:
                error_msg = f"Error in stream_joke: {str(e)}"
                logger.error(error_msg)
                yield f"Error: {error_msg}\n"
            
            finally:
                yield "\nEnd of stream\n"
                
        return StreamingResponse(
            event_generator(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting FastAPI app with client_mode={client_mode}, use_langgraph={use_langgraph}")
        
    return app
