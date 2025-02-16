# https://chatgpt.com/share/67ab0075-5950-800f-858a-b2b8dbd7de69
import asyncio
import openai
from langgraph.graph import StateGraph, START, END
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import os, httpx
# OPENAI_API_BASE_URL = "http://t1cim-wncchat.wneweb.com.tw/v1"
# ORION_CTH_API_KEY = os.environ['ORION_CTH_API_KEY']
# http_client = httpx.Client(verify=False)

client = openai.Client(   
# api_key=ORION_CTH_API_KEY,
# base_url=OPENAI_API_BASE_URL,
# http_client=http_client
)
    
# Your custom openai streaming call (blocking)
def call_openai_stream(prompt: str):
    # Initialize the OpenAI client
 
    return client.chat.completion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

# Async wrapper to convert blocking generator to async generator
async def async_generator_from(blocking_gen):
    loop = asyncio.get_running_loop()
    for item in blocking_gen:
        yield await loop.run_in_executor(None, lambda: item)

# Custom node function using openai driver directly
async def call_openai_node(state, config):
    prompt = state["prompt"]
    loop = asyncio.get_running_loop()
    # Run the blocking API call in an executor
    blocking_gen = await loop.run_in_executor(None, call_openai_stream, prompt)
    aggregated = ""
    # Use our async generator wrapper
    async for chunk in async_generator_from(blocking_gen):
        # The token is in chunk["choices"][0]["delta"]["content"]
        token = chunk["choices"][0]["delta"].get("content", "")
        # Log each token as it is streamed
        print(f"[STREAM] Token: {token}")
        aggregated += token
        # Yield each token wrapped in a dict for streaming events
        yield {"token": token}
    # Once done, return the aggregated result
    print("right before call_openai_node's return statement")
    return {"response": aggregated}

# Build your graph with the custom node
graph = (
    StateGraph(dict)
    .add_node(call_openai_node)
    .add_edge(START, "call_openai_node")
    .add_edge("call_openai_node", END)
    .compile()
)

# FastAPI example endpoint
app = FastAPI()

@app.get("/stream")
async def stream_endpoint(prompt: str = "Tell me a joke about cats"):
    async def event_generator():
        inputs = {"prompt": prompt}
        # Use stream_mode "messages" for token-level events
        async for event in graph.astream(inputs, stream_mode="messages"):
            # Each event is expected to have a 'token'
            if event.get("token"):
                yield f"{event['token']}\n"
    return StreamingResponse(event_generator(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run("openai_by_o3_mini:app", host="0.0.0.0", port=8000, reload=True)

