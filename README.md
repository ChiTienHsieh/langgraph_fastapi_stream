Below is a complete, detailed README.md that explains your project's purpose, folder structure, setup, usage, testing, and experimental matrix.

---

```markdown
# LangGraph FastAPI Streaming Experiments

This repository is an experimental playground to evaluate real-time token streaming from an LLM using various combinations of frameworks and clients. The project lets you toggle three independent options:

1. **Execution Mode:**  
   - Direct execution (CLI)  
   - FastAPI endpoint

2. **LangGraph Orchestration:**  
   - Using LangGraph  
   - Plain (direct) streaming implementation

3. **LLM Client:**  
   - Native OpenAI client  
   - LangChain's OpenAI client

These three binary choices yield 2 × 2 × 2 = 8 possible combinations. You can run and record the streaming behavior of each configuration from a single entry point (`main.py`).

## Folder Structure

```
langgraph_fastapi_stream/
├── main.py                   # Entry point to toggle between modes and configurations.
├── README.md                 # Project documentation.
├── requirements.txt          # Python dependencies.
├── .gitignore                # Files and directories to ignore.
├── src/                      # Contains the implementation modules.
│   ├── __init__.py
│   ├── direct_execution.py   # Direct (CLI) execution of streaming output.
│   ├── fastapi_endpoint.py   # FastAPI endpoint to serve streaming responses.
│   ├── langgraph_impl.py     # LangGraph orchestration implementation.
│   ├── plain_impl.py         # Plain streaming implementation (no LangGraph).
│   ├── openai_client.py      # Module using the async OpenAI client.
│   └── langchain_openai_client.py  # Module using the LangChain OpenAI client.
└── tests/                    # Pytest tests to verify all combinations.
    ├── __init__.py
    └── test_combinations.py  # Tests for the 8 streaming combinations.
```

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/ChiTienHsieh/langgraph_fastapi_stream.git
   cd langgraph_fastapi_stream
   ```

2. **Install Dependencies:**

   Ensure you have Python 3.10 or later. Then run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**

   Set your API key in the environment. For example, on a Unix system:

   ```bash
   export ORION_CTH_API_KEY="YOUR_API_KEY"
   ```

   (The async OpenAI client will use this key.)

## Running the Application

You can run the project in one of two modes—direct (CLI) execution or as a FastAPI endpoint.

### Direct Execution (CLI)

Run with direct mode:

```bash
python main.py --mode direct --client openai --langgraph --topic "dogs"
```

Options:
- `--client`: Choose between `openai` or `langchain`.
- `--langgraph`: Include this flag to use LangGraph orchestration (omit it for plain streaming).
- `--topic`: Topic to prompt the LLM (e.g., "dogs").

### FastAPI Endpoint

Run the FastAPI server:

```bash
python main.py --mode api --client openai --langgraph --topic "dogs" --host 0.0.0.0 --port 8000
```

Then access the streaming endpoint (for example, using curl):

```bash
curl -N "http://localhost:8000/stream?topic=dogs"
```

## Testing

Tests are written with pytest and pytest-asyncio. To run tests, first install pytest-asyncio if you haven’t already:

```bash
pip install pytest-asyncio
```

Then run:

```bash
pytest
```

## Experimental Matrix

Below is an overview of the 8 possible combinations. As you run experiments, fill in the "Streaming Works?" column with your observations.

| Combination | Execution Mode | LangGraph | LLM Client | Streaming Works? |
|-------------|----------------|-----------|------------|------------------|
| 1           | Direct         | Yes       | OpenAI     |                  |
| 2           | Direct         | Yes       | LangChain  |                  |
| 3           | Direct         | No        | OpenAI     |                  |
| 4           | Direct         | No        | LangChain  |                  |
| 5           | FastAPI        | Yes       | OpenAI     |                  |
| 6           | FastAPI        | Yes       | LangChain  |                  |
| 7           | FastAPI        | No        | OpenAI     |                  |
| 8           | FastAPI        | No        | LangChain  |                  |

## Contributing

Contributions, bug reports, and feature requests are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
```

---

This README.md provides a clear overview of your project, how to set it up and run it, and the experimental matrix you intend to use to record streaming behavior across all combinations. Adjust details as needed, and happy experimenting!