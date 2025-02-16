import os
import json
import pytest
import asyncio
from datetime import datetime
from src.openai_client import stream_openai_tokens

@pytest.mark.asyncio
async def test_record_openai_stream_responses():
    """
    Integration test that records real OpenAI streaming responses.
    This test requires:
    - A valid OpenAI API key in the environment
    - Network connectivity to OpenAI's API
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/openai_stream_{timestamp}.jsonl"
    
    chunks = []
    async for chunk in stream_openai_tokens("dogs"):
        # Record each chunk
        chunks.append(chunk)
        
        # Convert OpenAI object to JSON-serializable dict if it's not already a dict
        chunk_dict = chunk if isinstance(chunk, dict) else {
            'id': chunk.id,
            'object': chunk.object,
            'created': chunk.created,
            'model': chunk.model,
            'system_fingerprint': chunk.system_fingerprint,
            'choices': [{
                'index': choice.index,
                'delta': {
                    'role': choice.delta.role,
                    'content': choice.delta.content,
                    'function_call': choice.delta.function_call,
                    'tool_calls': choice.delta.tool_calls
                },
                'finish_reason': choice.finish_reason,
                'logprobs': choice.logprobs
            } for choice in chunk.choices]
        }
        
        # Write to log file
        with open(log_file, "a") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "chunk": chunk_dict
            }, f)
            f.write("\n")
    
    # Basic assertions to verify we got some chunks
    assert len(chunks) > 0, "No chunks received from OpenAI"
    
    # Log file information
    print(f"\nStream chunks recorded to: {log_file}")
    print(f"Total chunks recorded: {len(chunks)}")
    
    # Categorize responses
    completion_chunks = [c for c in chunks if not isinstance(c, dict)]
    error_chunks = [c for c in chunks if isinstance(c, dict) and "error" in c]
    
    print("\nResponse Statistics:")
    print(f"Completion chunks: {len(completion_chunks)}")
    print(f"Error chunks: {len(error_chunks)}")
    
    # Show example of first completion chunk if available
    if completion_chunks:
        first_chunk = completion_chunks[0]
        print("\nExample completion chunk:")
        print(f"ID: {first_chunk.id}")
        print(f"Model: {first_chunk.model}")
        print(f"Object type: {first_chunk.object}")
        if first_chunk.choices and first_chunk.choices[0].delta.content:
            print(f"Content: {first_chunk.choices[0].delta.content}")
    
    if error_chunks:
        print("\nExample error chunk:")
        print(json.dumps(error_chunks[0], indent=2))

@pytest.mark.asyncio
async def test_record_openai_stream_errors():
    """
    Test to trigger and record error responses from OpenAI streaming.
    Uses an invalid model name to force an error response.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/openai_stream_errors_{timestamp}.jsonl"
    
    # Temporarily modify the OpenAI client configuration
    from src.openai_client import openai_client
    original_model = "gpt-4-mini-2024-07-18"  # Store original model
    openai_client.model = "invalid-model-name"  # Set invalid model
    
    chunks = []
    try:
        async for chunk in stream_openai_tokens("dogs"):
            chunks.append(chunk)
            
            # Convert OpenAI object to JSON-serializable dict if it's not already a dict
            chunk_dict = chunk if isinstance(chunk, dict) else {
                'id': chunk.id,
                'object': chunk.object,
                'created': chunk.created,
                'model': chunk.model,
                'system_fingerprint': chunk.system_fingerprint,
                'choices': [{
                    'index': choice.index,
                    'delta': {
                        'role': choice.delta.role,
                        'content': choice.delta.content,
                        'function_call': choice.delta.function_call,
                        'tool_calls': choice.delta.tool_calls
                    },
                    'finish_reason': choice.finish_reason,
                    'logprobs': choice.logprobs
                } for choice in chunk.choices]
            }
            
            with open(log_file, "a") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "chunk": chunk_dict
                }, f)
                f.write("\n")
    finally:
        # Restore original model
        openai_client.model = original_model
    
    # Verify we got error responses
    assert any(isinstance(c, dict) and "error" in c for c in chunks), "No error chunks received"
    
    print(f"\nError chunks recorded to: {log_file}")
    print(f"Total chunks recorded: {len(chunks)}")
    
    error_chunks = [c for c in chunks if isinstance(c, dict) and "error" in c]
    if error_chunks:
        print("\nExample error chunk:")
        print(json.dumps(error_chunks[0], indent=2))
