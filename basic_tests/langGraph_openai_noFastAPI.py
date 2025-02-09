import asyncio
from langgraph.graph import StateGraph, START, END
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from openai import AsyncOpenAI

# Initialize OpenAI async client
openai_client = AsyncOpenAI()


async def stream_tokens(messages):
    """Streams tokens from OpenAI API."""
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    async for chunk in response:
        token = chunk.choices[0].delta.content
        if token:
            await asyncio.sleep(0.3)
            yield token


async def main():
    """Test LangGraph streaming WITHOUT FastAPI."""
    async for token in stream_tokens(
        [{"role": "user", "content": "Tell me a joke about cats"}]
    ):
        print(token, end="|", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
