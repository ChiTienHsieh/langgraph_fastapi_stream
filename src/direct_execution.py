# src/direct_execution.py
import asyncio
from src.langgraph_impl import build_langgraph
from src.plain_impl import stream_plain
from src.openai_client import stream_openai_tokens
from src.langchain_openai_client import stream_langchain_tokens

async def run_direct(client_mode: str = "openai", use_langgraph: bool = False, topic: str = "dogs"):
    # Select the appropriate client function.
    if client_mode == "openai":
        client_fn = stream_openai_tokens
    elif client_mode == "langchain":
        client_fn = stream_langchain_tokens
    else:
        raise ValueError("Invalid client_mode; choose 'openai' or 'langchain'.")

    if use_langgraph:
        print("Streaming via LangGraph:")
        graph = build_langgraph(client_fn)
        # Pass the client function via the config and inputs
        inputs = {
            "topic": topic,
            "client_fn": client_fn  # Pass client_fn in inputs instead of config
        }
        async for token_chunk, _ in graph.astream(inputs, stream_mode="custom"):
            print(token_chunk["token"], end="", flush=True)
    else:
        print("Streaming directly:")
        async for token in stream_plain(topic, client_fn):
            print(token, end="", flush=True)
    print()  # Newline after completion.
