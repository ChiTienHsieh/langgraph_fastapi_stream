# LLM Streaming Experiments

This repository is an experimental playground for testing different combinations of frameworks to stream Large Language Model (LLM) outputs. The goal is to explore the interplay between:

- **Web frameworks:** FastAPI (or running without a web server)
- **Graph orchestration:** LangGraph (or direct execution)
- **LLM API integration:** Direct OpenAI API calls vs. using LangChain wrappers

By mixing and matching these components, you can evaluate which architecture best supports token-by-token streaming and suits your application needs.

## Overview

The repository contains example implementations that demonstrate:
- A FastAPI endpoint that streams tokens from an LLM in real time.
- A LangGraph node to orchestrate and manage state between calls.
- Two methods for calling the LLM:
  - Using `openai.chat.completions.create` directly (with streaming enabled)
  - Using LangChain’s wrappers (see `api_w_LangChain.py` for an alternative approach)

Each experiment aims to help you understand the trade-offs between these combinations and serve as a reference for building interactive, real-time LLM applications.

## Directory Structure

```
.
├── api_w_openai.py         # FastAPI + LangGraph + OpenAI API streaming implementation
├── api_w_LangChain.py      # FastAPI + LangGraph + LangChain streaming implementation
├── README.md               # This file
└── requirements.txt        # Python dependencies for the project
```

## Prerequisites

- Python 3.10 or later
- An OpenAI API key (set in your environment variables)
- Required packages (listed in `requirements.txt`)

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/llm-streaming-experiments.git
cd llm-streaming-experiments
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the FastAPI Endpoints

#### OpenAI API + LangGraph (Direct API Call)
Run the FastAPI server with:

```bash
uvicorn api_w_openai:app --reload
```

Then access the endpoint (for example, using curl):

```bash
curl -N "http://localhost:8000/stream?topic=dogs"
```

#### LangChain + LangGraph (Alternative Approach)
If you want to try the LangChain-based approach, run:

```bash
uvicorn api_w_LangChain:app --reload
```

and access the appropriate endpoint.

### Running Without FastAPI

If you prefer to experiment without a web framework (i.e. run your nodes as standalone scripts), you can modify the example scripts to call their main functions directly. This might help isolate issues related to streaming versus web server behavior.

## Experimentation Goals

- **FastAPI or not:** Evaluate whether wrapping the streaming output in a web framework affects performance or behavior.
- **LangGraph or not:** Determine how well LangGraph orchestrates token streaming compared to a direct call approach.
- **openai or LangChain:** Compare using the OpenAI API directly with a LangChain wrapper for LLM calls.

This repository is intended as a reference for building real-time interactive applications (like chatbots or live data dashboards) that require incremental token streaming from LLMs.

## Contributing

Contributions, bug reports, and feature requests are welcome. Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
```

Feel free to modify this README to better suit your project's specifics or add any additional details about your experiments. Happy coding and experimenting!