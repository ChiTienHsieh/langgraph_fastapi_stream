# src/plain_impl.py
async def stream_plain(topic: str, client_fn):
    """
    Directly streams tokens from the client function.
    client_fn is expected to be an async generator function.
    """
    async for token in client_fn(topic):
        yield token
