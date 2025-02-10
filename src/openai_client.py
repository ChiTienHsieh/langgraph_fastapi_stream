# src/openai_client.py
import os
import asyncio
import httpx
from typing import AsyncGenerator
from openai import AsyncOpenAI  # Ensure you have an async OpenAI client installed
from langchain_core.runnables import RunnableConfig

# Configuration for the async OpenAI client.
OPENAI_API_BASE_URL = "http://t1cim-wncchat.wneweb.com.tw/v1"
# ORION_CTH_API_KEY = os.environ['ORION_CTH_API_KEY']

# Create an async HTTP client with SSL verification enabled
http_client = httpx.AsyncClient()
# For disabling SSL verification when needed:
# http_client = httpx.AsyncClient(verify=False)

# Initialize the async OpenAI client.
openai_client = AsyncOpenAI(
    # api_key=ORION_CTH_API_KEY,
    # base_url=OPENAI_API_BASE_URL,
    http_client=http_client
)

async def stream_openai_tokens(topic: str, config: RunnableConfig = None) -> AsyncGenerator[str, None]:
    """
    Streams tokens from the async LLM client.

    Args:
        topic (str): The topic for the joke.

    Yields:
        str: Each token (as a string) generated by the LLM.

    Raises:
        Exception: If there's an error during API communication or token streaming.
    """
    try:
        messages = [{"role": "user", "content": f"Tell me a joke about {topic}"}]
        # Call the async chat completions API with streaming enabled.
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            stream=True,
            timeout=30.0  # Add timeout for API calls
        )
        
        # Track if we've received any content
        content_received = False
        
        # Iterate asynchronously over the streaming response.
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content_received = True
                # Add a short delay to simulate real-time streaming.
                await asyncio.sleep(0.1)
                yield chunk.choices[0].delta.content
        
        # If we haven't received any content, raise an error
        if not content_received:
            raise Exception("No content received from API")
            
        # Always yield end marker after successful streaming
        yield "\n\n End of stream"
            
    except Exception as e:
        # Log the error and re-raise
        print(f"Error in stream_openai_tokens: {str(e)}")
        raise
