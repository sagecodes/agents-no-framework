import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

# ------------------------------
# Tool Registry & Decorator
# ------------------------------
tool_registry = {}

def tool(fn):
    tool_registry[fn.__name__] = fn
    return fn

@tool
def add(a, b):
    """Adds two numbers and returns the result."""
    return a + b

@tool
def subtract(a, b):
    """Subtracts the second number from the first and returns the result."""
    return a - b

@tool
def multiply(a, b):
    """Multiplies two numbers and returns the result."""
    return a * b

@tool
def divide(a, b):
    """Divides the first number by the second. Raises error if divide by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@tool
def power(a, b):
    """Raises the first number to the power of the second and returns the result."""
    return a ** b

tool_descriptions = {name: fn.__doc__.strip() for name, fn in tool_registry.items()}
memory_log = []

# ------------------------------
# Agent Registry & Decorator
# ------------------------------
agent_registry = {}

def agent(name):
    def decorator(fn):
        agent_registry[name] = fn
        return fn
    return decorator

# ------------------------------
# Logger
# ------------------------------
class Logger:
    def __init__(self, path="agent_trace_log.jsonl"):
        self.path = path

    async def log(self, **kwargs):
        kwargs["timestamp"] = datetime.utcnow().isoformat()
        print("[LOG]", kwargs)
        with open(self.path, "a") as f:
            f.write(json.dumps(kwargs) + "\n")

logger = Logger()

# ------------------------------
# Planner Agent (routes to math or memory)
# ------------------------------
@agent("planner")
async def planner_agent(prompt, memory_log):
    recent = "\n".join([f"- {q} → {r}" for q, r in memory_log[-5:]]) or "No history."
    available = "\n".join([f"- {a}" for a in agent_registry.keys() if a != "planner"])
    system_msg = (
        f"You are a routing agent.\nAvailable agents:\n{available}\n\n"
        f"Recent memory:\n{recent}\n\n"
        f"Decide which agent to use and what task to pass it.\n"
        f"Return JSON like: {{\"agent\": \"math\", \"task\": \"Add 3 and 5\"}}"
    )
    res = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(res.choices[0].message.content)

# ------------------------------
# Memory Agent
# ------------------------------
@agent("memory")
async def memory_agent(task, memory_log):
    if not memory_log:
        return {"result": "Memory is empty."}
    task = task.lower()
    try:
        if "question" in task:
            return {"result": memory_log[-1][0]}
        elif "answer" in task or "result" in task:
            return {"result": memory_log[-1][1]}
        else:
            index = int(task)
            return {"result": memory_log[index][1]}
    except:
        return {"result": f"Memory access unclear: {task}"}

# ------------------------------
# Math Agent (delegates to tool reasoning)
# ------------------------------
@agent("math")
async def math_agent(prompt, memory_log):
    return await execute_plan(prompt)

# ------------------------------
# Router
# ------------------------------
async def multi_agent_router(prompt):
    plan = await agent_registry["planner"](prompt, memory_log)
    target = plan.get("agent")
    task = plan.get("task")

    if target not in agent_registry:
        return {"error": f"Unknown agent '{target}'. Available: {list(agent_registry.keys())}"}

    result = await agent_registry[target](task, memory_log)

    if target != "planner" and isinstance(result, dict) and "result" in result:
        memory_log.append((prompt, result["result"]))

    return result

# ------------------------------
# Tool Planner (LLM decides tool call steps)
# ------------------------------
async def get_tool_plan(user_prompt):
    tool_list = "\n".join([f"{name}: {desc}" for name, desc in tool_descriptions.items()])
    system_msg = (
        "You are a math reasoning agent. Break the user's prompt into tool calls.\n"
        "Available tools:\n"
        f"{tool_list}\n\n"
        "Return JSON like:\n"
        '[{"tool": "add", "args": [3, 5], "reasoning": "add 3 and 5"},\n'
        ' {"tool": "multiply", "args": ["previous", 2], "reasoning": "scale result"}]'
    )
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )
    raw = response.choices[0].message.content
    print("\n[LLM RAW PLAN]\n", raw)
    return json.loads(raw)

# ------------------------------
# Tool Executor
# ------------------------------
async def execute_plan(user_prompt):
    steps_log = []
    last_result = None

    try:
        plan = await get_tool_plan(user_prompt)

        for step in plan:
            tool_name = step["tool"]
            args = step["args"]
            reasoning = step.get("reasoning", "")
            args = [last_result if str(a).lower() == "previous" else a for a in args]

            if tool_name == "memory":
                result = await memory_agent(" ".join(str(a) for a in args), memory_log)
            elif tool_name in tool_registry:
                result = tool_registry[tool_name](*args)
            else:
                await logger.log(tool=tool_name, args=args, error="Unknown tool", reasoning=reasoning)
                raise ValueError(f"Unknown tool: {tool_name}")

            await logger.log(tool=tool_name, args=args, result=result, reasoning=reasoning)

            steps_log.append({
                "tool": tool_name,
                "args": args,
                "result": result,
                "reasoning": reasoning
            })

            last_result = result

        if steps_log:
            memory_log.append((user_prompt, steps_log[-1]["result"]))

        return {"final_result": last_result, "steps": steps_log}

    except Exception as e:
        await logger.log(
            tool=tool_name if "tool_name" in locals() else "unknown",
            args=args if "args" in locals() else [],
            error=e
        )
        return {"error": str(e), "steps": steps_log}

# ------------------------------
# CLI
# ------------------------------
async def main():
    while True:
        prompt = input("\nAsk something (or type 'exit'): ")
        if prompt.lower() == "exit":
            break
        result = await multi_agent_router(prompt)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise

# python 2_simple_agent_decorators agent.py