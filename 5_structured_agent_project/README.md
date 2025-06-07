# Structured Agent Project

This project is a multi-agent system designed to handle various tasks using specialized agents and tools. It is built with extensibility in mind, allowing developers to easily add new tools and agents to expand its capabilities.

## Features
- **Planner Agent**: Routes tasks to the appropriate agent based on the input prompt.
- **Math Agent**: Performs mathematical operations like addition, multiplication, and exponentiation.
- **String Agent**: Handles string-related tasks such as word and letter counting.
- **RAG Agent**: Integrates with a vector database for retrieval-augmented generation tasks.
- **Memory Agent**: Provides short-term memory functionality for referencing past interactions.

## Project Structure
```
5_structured_agent_project/
├── agents/                # Contains agent implementations
│   ├── math_agent.py
│   ├── memory_agent.py
│   ├── planner_agent.py
│   ├── rag_agent.py
│   └── string_agent.py
├── tools/                 # Contains tool implementations
│   ├── math_tools.py
│   ├── rag_tools.py
│   └── string_tools.py
├── utils/                 # Utility modules
│   ├── decorators.py      # Decorators for registering tools and agents
│   ├── executor.py        # Execution utilities
│   └── logger.py          # Logging utilities
├── config.py              # Configuration settings
├── main.py                # Entry point for the application
├── vector_store.py        # Vector database integration
└── rag_setup/             # Setup scripts for RAG
    ├── __init__.py
    └── load_rag_data.py
```

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Application
To start the application, run:
```bash
python main.py
```

### Interacting with the System
- Type a prompt to ask the system to perform a task.
- Type `exit` to quit the application.

## Adding New Tools
To add a new tool:
1. Create a function in the appropriate file under the `tools/` directory or create a new file if necessary.
2. Decorate the function with `@tool` from `utils.decorators`. Optionally, specify the agent it belongs to using the `agent` parameter.

Example:
```python
from utils.decorators import tool

@tool(agent="math")
def subtract(a, b):
    """Subtracts two numbers."""
    return a - b
```

3. The tool will automatically be available to the specified agent.

## Adding New Agents
To add a new agent:
1. Create a function in the `agents/` directory.
2. Decorate the function with `@agent` from `utils.decorators` and provide a unique name for the agent.

Example:
```python
from utils.decorators import agent

@agent("example")
async def example_agent(prompt, memory_log):
    # Implement agent logic here
    return {"result": "Example result"}
```

3. Register the agent in the `agent_registry` in `main.py`:
```python
agent_registry["example"] = example_agent
```

## Logging
All interactions are logged in `agent_trace_log.jsonl` for debugging and auditing purposes.

