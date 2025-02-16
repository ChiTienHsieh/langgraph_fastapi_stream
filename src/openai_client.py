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

# Initialize the async OpenAI client with configurable model
class OpenAIStreamClient:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.model = 'gpt-4o-mini-2024-07-18'  # Default model
        
    async def stream_tokens(self, topic: str, config: RunnableConfig = None) -> AsyncGenerator[dict, None]:
        try:
            messages = [{"role": "user", "content": f"Tell me a joke about {topic}"}]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                timeout=30.0
            )
            
            async for chunk in response:
                yield chunk
                
        except Exception as e:
            # For errors, we still need to yield a dict since we can't create OpenAI objects
            error_msg = f"Connection error: {str(e)}"
            logger.error(f"Error in stream_tokens: {error_msg}")
            yield {"error": error_msg}

# Create a singleton instance
openai_client = OpenAIStreamClient()

async def stream_openai_tokens(topic: str, config: RunnableConfig = None) -> AsyncGenerator[dict, None]:
    """
    Public interface for streaming tokens from the OpenAI client.
    Delegates to the singleton client instance.
    """
    async for response in openai_client.stream_tokens(topic, config):
        yield response
