# OpenAI Stream Response Types Documentation
This document outlines the various response types that can be received from the OpenAI streaming API.

## Response Structure

The streaming API returns a sequence of ChatCompletionChunk objects.

### ChatCompletionChunk Structure

Each chunk has the following format:
```json
{
    "id": "chatcmpl-B1ZNZMTtramoZfDDWbxMhiODjmGXZ",
    "object": "chat.completion.chunk",
    "created": 1739714025,
    "model": "gpt-4-0125-preview",
    "system_fingerprint": null,
    "choices": [
        {
            "index": 0,
            "delta": {
                "role": "assistant",  // Only in first chunk, null afterward
                "content": "string",  // The actual token content
                "function_call": null,
                "tool_calls": null
            },
            "finish_reason": null,  // null during streaming, "stop" in final chunk
            "logprobs": null
        }
    ]
}
```

### Stream Sequence

1. Initial Chunk:
   - Contains role: "assistant"
   - Empty content
   - Sets up the completion context

2. Content Chunks:
   - Each chunk contains a piece of the response
   - role is null
   - content contains the actual token text

3. Final Chunk:
   - Marks completion with finish_reason: "stop"
   - Empty content
   - Signals end of stream

### Error Responses

When errors occur, the stream yields error objects:

```json
{
    "error": "Connection error: Error code: 404 - {'error': {'message': 'The model `invalid-model-name` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}"
}
```

Common error scenarios:
- Invalid model name: 404 error with model_not_found code
- Authentication errors: 401 Unauthorized
- API rate limits: 429 Too Many Requests
- Network connectivity issues: Connection timeout errors
- Malformed requests: 400 Bad Request

## Log File Format

The test suite records responses to JSONL files in the `logs/` directory. Each line contains:
```json
{
    "timestamp": "ISO-8601 datetime",
    "chunk": {
        // The complete ChatCompletionChunk object or error response
    }
}
```

## Running Tests

To capture actual response types:

```bash
# Run all OpenAI stream response tests
pytest tests/test_openai_stream_responses.py -v

# Run specific test
pytest tests/test_openai_stream_responses.py::test_record_openai_stream_responses -v
pytest tests/test_openai_stream_responses.py::test_record_openai_stream_errors -v
```

Requirements:
- Valid OpenAI API key in environment
- Network connectivity
- pytest and pytest-asyncio installed

## Implementation Details

The streaming implementation in `src/openai_client.py`:
- Uses AsyncOpenAI client for streaming
- Preserves complete ChatCompletionChunk objects
- Handles both successful and error cases
- Supports configurable model selection
- Records raw response objects for analysis

Note: This documentation is based on actual recorded API responses, making it a reliable reference for the OpenAI streaming API's behavior.
