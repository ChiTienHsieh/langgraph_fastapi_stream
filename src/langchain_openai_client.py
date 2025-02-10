# src/langchain_openai_client.py
import asyncio
import os
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

class QueueCallbackHandler(BaseCallbackHandler):
    """Callback handler that pushes tokens to an asyncio queue."""
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs):
        # Push the token to the queue.
        await self.queue.put(token)
        # Increase delay to simulate real-time streaming.
        await asyncio.sleep(0.2)  # Adjust delay as needed

async def stream_langchain_tokens(topic: str) -> AsyncGenerator[str, None]:
    """
    Streams tokens using LangChain's ChatOpenAI client with streaming enabled.
    Tokens are yielded as they are received via the callback.
    """
    queue = asyncio.Queue()
    handler = QueueCallbackHandler(queue)
    
    # Initialize the model with streaming enabled and our callback.
    model = ChatOpenAI(
        model="gpt-4o-mini-2024-07-18", 
        streaming=True, 
        callbacks=[handler],
        base_url="http://t1cim-wncchat.wneweb.com.tw/v1", 
        api_key=os.environ['ORION_CTH_API_KEY']
    )
    
    # Run the model invocation in the background.
    generate_task = asyncio.create_task(
        model.ainvoke([{"role": "user", "content": f"Tell me a joke about {topic}"}])
    )
    
    # Create a background task that waits for the generation to complete,
    # then pushes a sentinel value (None) into the queue.
    async def put_sentinel():
        await generate_task
        await queue.put(None)
    
    asyncio.create_task(put_sentinel())
    
    # Consume tokens from the queue as they arrive.
    while True:
        token = await queue.get()
        if token is None:
            break
        # Optionally add a small delay in the consumer loop.
        await asyncio.sleep(0.1)
        yield token
