# src/langchain_openai_client.py
import asyncio
import os
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnableConfig
import httpx

# For disabling SSL verification when needed:
# http_client = httpx.AsyncClient(verify=False)

class QueueCallbackHandler(BaseCallbackHandler):
    """Callback handler that pushes tokens to an asyncio queue."""
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs):
        # Push the token to the queue with content wrapper
        await self.queue.put({"content": token})
        await asyncio.sleep(0.1)

async def stream_langchain_tokens(topic: str, config: RunnableConfig = None) -> AsyncGenerator[dict, None]:
    """
    Streams tokens using LangChain's ChatOpenAI client with streaming enabled.
    Tokens are yielded as they are received via the callback.

    Args:
        topic (str): The topic for the joke.
        config (RunnableConfig, optional): Configuration for the runnable.

    Yields:
        dict: Each token wrapped in a dict with 'content' or 'error' key
    """
    queue = asyncio.Queue()
    handler = QueueCallbackHandler(queue)
    content_received = False
    error = None

    try:
        model = ChatOpenAI(
            model="gpt-4o-mini-2024-07-18",
            streaming=True,
            callbacks=[handler],
            request_timeout=30.0,
            # base_url="http://t1cim-wncchat.wneweb.com.tw/v1", 
            # api_key=os.environ['ORION_CTH_API_KEY'],
            # http_async_client=http_client
        )

        generate_task = asyncio.create_task(
            model.ainvoke(
                [{"role": "user", "content": f"Tell me a joke about {topic}"}],
                config=config
            )
        )

        async def put_sentinel():
            try:
                await generate_task
                await queue.put(None)
            except Exception as e:
                nonlocal error
                error = e
                await queue.put(None)

        sentinel_task = asyncio.create_task(put_sentinel())

        while True:
            try:
                token = await asyncio.wait_for(queue.get(), timeout=30.0)
                if token is None:
                    break
                if isinstance(token, dict) and "content" in token:
                    content_received = True
                    yield token
            except asyncio.TimeoutError:
                yield {"error": "Timeout waiting for tokens"}
                break

        if error:
            yield {"error": f"Error during generation: {str(error)}"}
        elif not content_received:
            yield {"error": "No content received from API"}

    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"Error in stream_langchain_tokens: {error_msg}")
        yield {"error": error_msg}

    finally:
        if 'generate_task' in locals():
            generate_task.cancel()
        if 'sentinel_task' in locals():
            sentinel_task.cancel()
