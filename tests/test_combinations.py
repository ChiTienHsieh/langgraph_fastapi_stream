import pytest
import asyncio
from fastapi.testclient import TestClient

# Import functions from your src modules.
from src.direct_execution import run_direct
from src.fastapi_endpoint import create_app

# -------------------------------
# Test for Direct Execution Mode
# -------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("client_mode,use_langgraph", [
    ("openai", True),
    ("langchain", True),
    ("openai", False),
    ("langchain", False),
])
async def test_direct_execution(capsys, client_mode, use_langgraph):
    """
    Runs the direct execution (CLI) mode and captures stdout.
    Expects that some non-empty output (i.e. streaming tokens and end marker)
    is printed to stdout.
    """
    await run_direct(client_mode=client_mode, use_langgraph=use_langgraph, topic="test")
    # Capture the printed output
    captured = capsys.readouterr().out
    # Log the captured output for debugging
    print(f"[Direct Execution] (client_mode={client_mode}, langgraph={use_langgraph}):")
    print(captured)
    # Assert that we did get meaningful output beyond just headers
    output = captured.strip()
    if use_langgraph:
        assert "Streaming via LangGraph:" in output, "Missing LangGraph header"
        # Remove the header to check actual content
        content = output.replace("Streaming via LangGraph:", "").strip()
        assert content != "", "LangGraph execution produced no content beyond header"
    else:
        assert "Streaming directly:" in output, "Missing direct streaming header"
        # Remove the header to check actual content
        content = output.replace("Streaming directly:", "").strip()
        assert content != "", "Direct execution produced no content beyond header"

# -------------------------------
# Test for FastAPI Endpoint Mode
# -------------------------------

@pytest.mark.parametrize("client_mode,use_langgraph", [
    ("openai", True),
    ("langchain", True),
    ("openai", False),
    ("langchain", False),
])
def test_api_endpoint(client_mode, use_langgraph):
    """
    Creates the FastAPI app for the given configuration,
    calls the /stream endpoint, and streams the output directly.
    Expects a 200 response and successful streaming.
    """
    app = create_app(client_mode=client_mode, use_langgraph=use_langgraph)
    client = TestClient(app)
    with client.stream("GET", "/stream?topic=test") as response:
        assert response.status_code == 200, "API endpoint did not return 200 OK."

        # Stream the output directly
        print(f"\n[API Endpoint] (client_mode={client_mode}, langgraph={use_langgraph}):")
        # Stream and check content
        content_received = False
        content = ""
        
        for chunk in response.iter_text():
            content += chunk
            print(chunk, end="", flush=True)
            
            # For LangGraph, we need to check for meaningful content beyond the "No content" message
            if use_langgraph:
                if chunk.strip() and "No content received from LLM" not in chunk:
                    content_received = True
            else:
                if chunk.strip():
                    content_received = True
        
        if use_langgraph:
            assert content_received, "LangGraph API endpoint returned no meaningful content"
        else:
            assert content_received, "API endpoint returned no content"
