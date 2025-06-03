# Simple AI Agent with no framework

continuations of the simple agent that calls different functions for calculator capabilities, but adds a very basic short term memory feature to reference previous questions and results.  

Features:
- Read in doc strings from functions for LLM to know about features.
- Provide tool list & doc strings into prompt
- Log each run and provide reasoning in log to help debug agent
- Simple short term memory

I'm using OpenAI API for this example, but can be changeg out for self hosted or other APIs

- set `OPENAI_API_KEY=YOURKEY` in .env

Run AI Agent:

- `python 1_simple_agent_memory/agent.py`