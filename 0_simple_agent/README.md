# Simple AI Agent with no framework

A simple agent that calls different functions for calculator capabilities.

Features:
- Read in doc strings from functions for LLM to know about features.
- Provide tool list & doc strings into prompt
- Log each run and provide reasoning in log to help debug agent

I'm using OpenAI API for this example, but can be changeg out for self hosted or other APIs

- set `OPENAI_API_KEY=YOURKEY` in .env

Run AI Agent:

- `python 0_simple_agent/function_agent.py `