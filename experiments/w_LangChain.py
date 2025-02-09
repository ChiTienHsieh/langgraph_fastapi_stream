import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Initialize the ChatOpenAI model with streaming enabled
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)


# In Python 3.10, our node function must accept the extra config parameter
async def call_model(state, config):
    topic = state["topic"]
    # Manually pass the config to ensure callbacks propagate
    response = await model.ainvoke(
        [{"role": "user", "content": f"Tell me a joke about {topic}"}], config=config
    )
    # Print streamed output if desired (here, response.content aggregates tokens)
    return {"joke": response.content}


# Build the graph
graph = (
    StateGraph(dict)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .add_edge("call_model", END)
    .compile()
)


async def main():
    inputs = {"topic": "dogs"}
    # Create a dummy config (LangChain typically manages this internally)
    config = {}
    async for msg, metadata in graph.astream(inputs, stream_mode="messages"):
        # print("Streamed message chunk:", msg)
        # wait for 0.3 seconds to simulate processing time
        await asyncio.sleep(0.3)
        if msg.content:
            print("\nFinal joke:", msg.content)


if __name__ == "__main__":
    asyncio.run(main())
