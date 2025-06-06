from utils.decorators import agent, agent_tools
from utils.executor import execute_plan

@agent("string")
async def string_agent(prompt, memory_log):
    toolset = agent_tools["string"]  # ✅ correct way
    tool_list = "\n".join([f"{name}: {fn.__doc__.strip()}" for name, fn in toolset.items()])
    system_msg = (
        "You are a string analysis agent. You can count letters, words, and analyze text.\n"
        "For each step, include a 'reasoning' field explaining why this tool is being called.\n\n"
        f"Tools:\n{tool_list}\n\n"
        "Return a list of tool calls like:\n"
        '[\n'
        '  {"tool": "word_count", "args": ["hello world"], "reasoning": "Counting words in the input string."},\n'
        '  {"tool": "letter_count", "args": ["previous"], "reasoning": "Counting letters in the previous result."}\n'
        ']\n'
        "IMPORTANT: Always include a 'reasoning' field explaining why this tool is being called."
    )
    return await execute_plan(prompt, agent="string", system_msg=system_msg)
