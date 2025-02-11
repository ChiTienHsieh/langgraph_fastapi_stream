# src/plain_impl.py
from typing import AsyncGenerator, Union, Dict, Any

async def stream_plain(topic: str, client_fn) -> AsyncGenerator[str, None]:
    """
    Directly streams tokens from the client function.
    client_fn is expected to be an async generator function.
    
    Args:
        topic: The topic to generate content about
        client_fn: An async generator function that yields tokens
        
    Yields:
        Tokens from the client function, with error handling
    """
    try:
        async for token in client_fn(topic):
            if isinstance(token, dict):
                if "error" in token:
                    yield f"Error: {token['error']}"
                elif "content" in token:
                    yield token["content"]
            elif isinstance(token, str):
                yield token
            
    except Exception as e:
        yield f"Error in stream_joke: {str(e)}"
