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
            if use_langgraph:
                graph = build_langgraph(client_fn)
                config = {"client_fn": client_fn}
                inputs = {"topic": topic}
                async for token_chunk, _ in graph.astream(inputs, stream_mode="custom"):
                    yield token_chunk["token"]
                    await asyncio.sleep(0.01)
            else:
                async for token in stream_plain(topic, client_fn):
                    yield token
                    await asyncio.sleep(0.01)
        return StreamingResponse(event_generator(), media_type="text/plain")
    return app
