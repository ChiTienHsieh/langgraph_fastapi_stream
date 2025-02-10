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
    # Assert that we did get some output.
    assert captured.strip() != "", "Direct execution produced empty output."

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
    response = client.get("/stream?topic=test", stream=True)
    
    assert response.status_code == 200, "API endpoint did not return 200 OK."

    # Stream the output directly
    print(f"\n[API Endpoint] (client_mode={client_mode}, langgraph={use_langgraph}):")
    content_received = False
    for chunk in response.iter_text():
        print(chunk, end="", flush=True)
        if chunk.strip():
            content_received = True
    
    assert content_received, "API endpoint returned no content"
