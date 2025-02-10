# main.py
import argparse
import asyncio
import uvicorn
from src.direct_execution import run_direct
from src.fastapi_endpoint import create_app

def main():
    parser = argparse.ArgumentParser(description="LLM Streaming Experiments")
    parser.add_argument("--mode", choices=["direct", "api"], default="direct",
                        help="Execution mode: direct CLI or FastAPI endpoint")
    parser.add_argument("--client", choices=["openai", "langchain"], default="openai",
                        help="LLM client to use for streaming")
    parser.add_argument("--langgraph", action="store_true",
                        help="Use LangGraph orchestration if set")
    parser.add_argument("--topic", default="dogs", help="Topic for the joke")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API mode")
    args = parser.parse_args()

    if args.mode == "direct":
        asyncio.run(run_direct(client_mode=args.client,
                               use_langgraph=args.langgraph,
                               topic=args.topic))
    elif args.mode == "api":
        app = create_app(client_mode=args.client,
                         use_langgraph=args.langgraph)
        uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
