# a working case of LangChain + LangGraph + OpenAI API
import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

app = FastAPI()

import os, httpx
OPENAI_API_BASE_URL = "http://t1cim-wncchat.wneweb.com.tw/v1"
ORION_CTH_API_KEY = os.environ['ORION_CTH_API_KEY']
http_client = httpx.Client(verify=False)

# Initialize the ChatOpenAI model with streaming enabled
model = ChatOpenAI(model="gpt-4o-mini-2024-07-18", streaming=True, api_key=ORION_CTH_API_KEY, base_url=OPENAI_API_BASE_URL, http_client=http_client)


# In Python 3.10, our node function must accept the extra config parameter
async def call_model(state, config: RunnableConfig):
    topic = state["topic"]
    # Manually pass the config to ensure callbacks propagate
    response = await model.ainvoke(
        [{"role": "user", "content": f"Tell me a joke about {topic}"}], config=config
    )

    # print to see the order
    print("right before call_model's return statement") 
    # The response's content aggregates the streamed tokens
    return {"joke": response.content}


# Build the graph
graph = (
    StateGraph(dict)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .add_edge("call_model", END)
    .compile()
)


@app.get("/stream")
async def stream_joke(topic: str = Query("dogs", description="Topic for the joke")):
    """
    Endpoint that streams a joke generated by LangChain + LangGraph.
    """

    async def event_generator():
        # Prepare inputs and config
        inputs = {"topic": topic}
        # config: RunnableConfig = {}  # Dummy config; typically managed internally by LangChain
        # Iterate over the streamed messages from the graph
        async for msg, metadata in graph.astream(inputs, stream_mode="messages"):
            # Optionally simulate processing delay
            await asyncio.sleep(0.3)
            if msg.content:
                print(f"[STREAM] Token: {msg.content}")  # Log the toke
                # Yield each chunk of content followed by a newline
                yield f"{msg.content}\n"

    # Return a streaming response with the appropriate media type.
    # You could also use "text/event-stream" if you wish to support SSE.
    return StreamingResponse(event_generator(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_w_langchain:app", host="0.0.0.0", port=8000, reload=True)