import asyncio
import json
import os
from datetime import datetime
import sys
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# ------------------------------
# OpenAI API Setup | Can adjust to different LLM providers
# ------------------------------
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)  # Async client for OpenAI API if using notebook


# ------------------------------
# Define Tool Functions
# Each has a docstring used for LLM context
# ------------------------------
def add(a, b):
    """Adds two numbers and returns the result."""
    return a + b


def subtract(a, b):
    """Subtracts the second number from the first and returns the result."""
    return a - b


def multiply(a, b):
    """Multiplies two numbers and returns the result."""
    return a * b


def divide(a, b):
    """Divides the first number by the second. Raises error if divide by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def power(a, b):
    """Raises the first number to the power of the second and returns the result."""
    return a**b


# Register tools dynamically
tools = {fn.__name__: fn for fn in [add, subtract, multiply, divide, power]}
tool_descriptions = {name: fn.__doc__.strip() for name, fn in tools.items()}

# ------------------------------
# Simple in-memory history
# ------------------------------
memory_log = []  # Stores (user_prompt, result_summary)


def handle_memory_tool(args):
    if not memory_log:
        return "Memory is empty."

    key = args[0].lower() if args else "last"

    if "question" in key:
        return memory_log[-1][0]  # Last user question
    elif "answer" in key or "result" in key:
        return memory_log[-1][1]  # Last answer
    elif key.isdigit() or key.startswith("-"):
        index = int(key)
        if abs(index) <= len(memory_log):
            return memory_log[index][1]
        else:
            return f"No memory at index {index}."
    else:
        return f"Unknown memory reference: {key}"


# ------------------------------
# Ask LLM to plan tool calls
# Returns list of steps with optional `reasoning` field
# ------------------------------
async def decide_plan_async(user_prompt):
    # Create a summary of all available tools with descriptions
    tool_list = "\n".join(
        [f"{name}: {desc}" for name, desc in tool_descriptions.items()]
    )

    system_msg = (
        "You are an AI reasoning agent that breaks a user's math question into a sequence of tool calls.\n"
        "Tools available:\n"
        f"{tool_list}\n\n"
        "For each step, explain WHY you're choosing that tool and what you're trying to accomplish in a 'reasoning' field.\n"
        "Return JSON like this:\n"
        '[{"tool": "add", "args": [3, 5], "reasoning": "using add to compute sum of 3 and 5"},\n'
        ' {"tool": "multiply", "args": ["previous", 2], "reasoning": "scaling the result by 2"}]\n'
        "To refer to memory, use the 'memory' tool like this:\n"
        '[{"tool": "memory", "args": ["last question"]}]\n'
        "Respond with ONLY valid JSON and nothing else."
    )

    # Call OpenAI with the system and user messages
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )

    # Grab and parse the plan JSON
    raw_response = response.choices[0].message.content
    print("\n[LLM RAW PLAN]\n", raw_response)  # Debugging: Show full plan
    return json.loads(raw_response)


# ------------------------------
# Logging Function
# Writes each tool step to a JSONL log
# ------------------------------
async def log_tool_call(tool_name, args, result=None, error=None, reasoning=None):
    timestamp = datetime.utcnow().isoformat()
    log = {
        "timestamp": timestamp,
        "tool": tool_name,
        "args": args,
        "result": result,
        "error": str(error) if error else None,
        "reasoning": reasoning,
    }
    print("[LOG]", log)
    with open("agent_trace_log.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")


# ------------------------------
# Main reasoning executor
# Parses plan, resolves args, executes tools, logs each step
# ------------------------------
async def run_reasoning_agent_async(user_prompt):
    steps_log = []
    last_result = None

    try:
        plan = await decide_plan_async(user_prompt)

        for step in plan:
            tool_name = step["tool"]
            args = step["args"]
            reasoning = step.get("reasoning", "")

            # Replace "previous" with the result of the last step
            args = [
                last_result if str(arg).lower() == "previous" else arg for arg in args
            ]

            # Handle tool calls
            if tool_name == "memory":
                result = handle_memory_tool(args)
            elif tool_name in tools:
                result = tools[tool_name](*args)
            else:
                await log_tool_call(
                    tool_name, args, error="Unknown tool", reasoning=reasoning
                )
                raise ValueError(f"Unknown tool: {tool_name}")

            # result = tools[tool_name](*args)
            await log_tool_call(tool_name, args, result=result, reasoning=reasoning)

            steps_log.append(
                {
                    "tool": tool_name,
                    "args": args,
                    "result": result,
                    "reasoning": reasoning,
                }
            )

            last_result = result

        # Save to memory
        if steps_log:
            memory_log.append((user_prompt, steps_log[-1]["result"]))

        return {"final_result": last_result, "steps": steps_log}

    except Exception as e:
        await log_tool_call(
            tool_name if "tool_name" in locals() else "unknown",
            args if "args" in locals() else [],
            error=e,
        )
        return {"error": str(e), "steps": steps_log}


# ------------------------------
# Async-friendly interactive runner
# Should Works in both script and Jupyter
# ------------------------------
async def main():
    while True:
        prompt = input("\nAsk a multi-step math question (or type 'exit'): ")
        if prompt.lower() == "exit":
            break
        result = await run_reasoning_agent_async(prompt)
        print(json.dumps(result, indent=2))


# Run in script or fallback to notebook-safe execution
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # Handles Jupyter-like environments
            if sys.platform == "win32": # not tested on Windows yet
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise

# python 1_simple_agent_memory/agent.py
