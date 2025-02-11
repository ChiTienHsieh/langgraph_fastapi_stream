import pytest
import asyncio
import json
from fastapi.testclient import TestClient

# Import functions from your src modules.
from src.direct_execution import run_direct
from src.fastapi_endpoint import create_app

def is_meaningful_content(content: str) -> bool:
    """
    Check if the content is meaningful by verifying:
    1. It's not empty
    2. It's not just whitespace
    3. It's not just a generic error message
    4. It contains more than just basic punctuation
    """
    if not content or not content.strip():
        return False
        
    # List of common error messages or placeholder content
    error_patterns = [
        "No content received",
        "Error during token streaming",
        "Missing required state",
    ]
    
    for pattern in error_patterns:
        if pattern in content:
            return False
            
    # Check if content has actual words (more than just punctuation)
    words = [word for word in content.split() if any(c.isalnum() for c in word)]
    return len(words) > 0

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
    Validates that meaningful content is generated and properly streamed.
    """
    await run_direct(client_mode=client_mode, use_langgraph=use_langgraph, topic="test")
    captured = capsys.readouterr().out
    print(f"[Direct Execution] (client_mode={client_mode}, langgraph={use_langgraph}):")
    print(captured)
    
    output = captured.strip()
    if use_langgraph:
        assert "Streaming via LangGraph:" in output, "Missing LangGraph header"
        content = output.replace("Streaming via LangGraph:", "").strip()
        
        # Check for error messages
        if "error" in content.lower():
            pytest.fail(f"LangGraph execution encountered an error: {content}")
            
        assert is_meaningful_content(content), (
            "LangGraph execution did not produce meaningful content. "
            f"Received: {content}"
        )
    else:
        assert "Streaming directly:" in output, "Missing direct streaming header"
        content = output.replace("Streaming directly:", "").strip()
        assert is_meaningful_content(content), (
            "Direct execution did not produce meaningful content. "
            f"Received: {content}"
        )

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
    Tests the FastAPI streaming endpoint with enhanced content validation.
    Verifies that the streamed content is meaningful and error-free.
    """
    app = create_app(client_mode=client_mode, use_langgraph=use_langgraph)
    client = TestClient(app)
    
    with client.stream("GET", "/stream?topic=test") as response:
        assert response.status_code == 200, "API endpoint did not return 200 OK."
        print(f"\n[API Endpoint] (client_mode={client_mode}, langgraph={use_langgraph}):")
        
        content = ""
        error_detected = False
        
        for chunk in response.iter_text():
            content += chunk
            print(chunk, end="", flush=True)
            
            # Check for error messages in the chunk
            if "error" in chunk.lower():
                error_message = chunk.strip()
                error_detected = True
                pytest.fail(f"Error in stream: {error_message}")
        
        # Validate the complete content
        assert is_meaningful_content(content), (
            f"API endpoint did not produce meaningful content. Mode: {client_mode}, "
            f"LangGraph: {use_langgraph}. Received: {content}"
        )
        
        if use_langgraph and not error_detected:
            # Additional validation for LangGraph responses
            try:
                # Try to parse any JSON content if present
                json_content = json.loads(content)
                assert "error" not in json_content, f"Error in response: {json_content['error']}"
            except json.JSONDecodeError:
                # Not JSON content, which is fine - just validate it's meaningful
                pass
