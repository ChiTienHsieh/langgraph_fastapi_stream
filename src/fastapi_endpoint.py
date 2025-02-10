# src/fastapi_endpoint.py
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import asyncio
from src.langgraph_impl import build_langgraph
from src.plain_impl import stream_plain
from src.openai_client import stream_openai_tokens
from src.langchain_openai_client import stream_langchain_tokens

def create_app(client_mode: str = "openai", use_langgraph: bool = False):
    app = FastAPI()
    # Select client function based on flag.
    if client_mode == "openai":
        client_fn = stream_openai_tokens
    elif client_mode == "langchain":
        client_fn = stream_langchain_tokens
    else:
        raise ValueError("Invalid client_mode. Use 'openai' or 'langchain'.")

    @app.get("/stream")
    async def stream_joke(topic: str = Query("dogs", description="Topic for the joke")):
        async def event_generator():
            try:
                if use_langgraph:
                    graph = build_langgraph(client_fn)
                    inputs = {
                        "topic": topic,
                        "client_fn": client_fn
                    }
                    content_received = False
                    async for token_chunk, _ in graph.astream(inputs, stream_mode="custom"):
                        content_received = True
                        yield token_chunk["token"]
                        await asyncio.sleep(0.01)
                    
                    # If no content was received, yield a message
                    if not content_received:
                        yield "No content received from LLM"
                    
                    # Always yield end marker
                    yield "\n\n End of stream"
                else:
                    content_received = False
                    async for token in stream_plain(topic, client_fn):
                        content_received = True
                        yield token
                        await asyncio.sleep(0.01)
                    
                    # If no content was received, yield a message
                    if not content_received:
                        yield "No content received from LLM"
                    
                    # Always yield end marker
                    yield "\n\n End of stream"
            except Exception as e:
                # Log the error and yield an error message
                print(f"Error in stream_joke: {str(e)}")
                yield f"Error: {str(e)}"
                
        return StreamingResponse(
            event_generator(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    return app
