# agents/math_agent.py

from utils.decorators import agent, agent_tools
from utils.executor import execute_plan

@agent("math")
async def math_agent(prompt, memory_log):
    toolset = agent_tools["math"]
    tool_list = "\n".join([f"{name}: {fn.__doc__.strip()}" for name, fn in toolset.items()])
    system_msg = (
        "You are a math agent that can solve arithmetic, powers, and multi-step problems.\n"
        "For each step, include a 'reasoning' field explaining why this tool is being called.\n\n"
        f"Tools:\n{tool_list}\n\n"
        "Return a list of tool calls like:\n"
        '[\n'
        '  {"tool": "add", "args": [2, 3], "reasoning": "Adding 2 and 3 to compute the sum."},\n'
        '  {"tool": "multiply", "args": ["previous", 5], "reasoning": "Multiplying previous result by 5."}\n'
        ']'
        "IMPORTANT: Always include a 'reasoning' field explaining why this tool is being called."
    )

    return await execute_plan(prompt, agent="math", system_msg=system_msg)
