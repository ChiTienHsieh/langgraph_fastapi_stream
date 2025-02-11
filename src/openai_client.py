# src/openai_client.py
import os
import asyncio
import httpx
import logging
from typing import AsyncGenerator
from openai import AsyncOpenAI  # Ensure you have an async OpenAI client installed
from langchain_core.runnables import RunnableConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for the async OpenAI client.
# OPENAI_API_BASE_URL = "http://t1cim-wncchat.wneweb.com.tw/v1"
# ORION_CTH_API_KEY = os.environ['ORION_CTH_API_KEY']

# Create an async HTTP client with SSL verification enabled
http_client = httpx.AsyncClient()
# For disabling SSL verification when needed:
# http_client = httpx.AsyncClient(verify=False)

# Initialize the async OpenAI client.
openai_client = AsyncOpenAI(
    # api_key=ORION_CTH_API_KEY,
    # base_url=OPENAI_API_BASE_URL,
    # http_client=http_client
)

async def stream_openai_tokens(topic: str, config: RunnableConfig = None) -> AsyncGenerator[dict, None]:
    """
    Streams tokens from the async LLM client.

    Args:
        topic (str): The topic for the joke.
        config (RunnableConfig, optional): Configuration for the runnable.

    Yields:
        dict: Each token wrapped in a dict with 'content' or 'error' key
    """
    try:
        messages = [{"role": "user", "content": f"Tell me a joke about {topic}"}]
        
        # Call the async chat completions API with streaming enabled
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            stream=True,
            timeout=30.0
        )
        
        full_response = ""
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield {"content": content}
        
        if not full_response.strip():
            logger.warning("No content received from OpenAI API")
            yield {"error": "No content received from API"}
            
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        logger.error(f"Error in stream_openai_tokens: {error_msg}")
        yield {"error": error_msg}
