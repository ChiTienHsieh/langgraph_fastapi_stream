#!/usr/bin/env python3
"""
Minimal FastAPI app that streams OpenAI API response.
"""

import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

# Initialize OpenAI async client
openai_client = AsyncOpenAI()

app = FastAPI(title="OpenAI Streaming API")


async def openai_token_generator(prompt: str):
    """
    Calls OpenAI API and streams tokens as they arrive.
    """
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,  # Enable streaming response
    )
    async for chunk in response:
        token = chunk.choices[0].delta.content
        if token:
            yield (token + " ").encode("utf-8")  # Yield token as bytes
            await asyncio.sleep(0)  # Ensures immediate streaming


@app.get("/stream", response_class=StreamingResponse)
async def stream_openai(prompt: str = Query(..., description="Prompt for OpenAI")):
    """
    Streams OpenAI's token output in real-time.
    """
    return StreamingResponse(
        openai_token_generator(prompt),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
