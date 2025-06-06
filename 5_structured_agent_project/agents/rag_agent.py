from utils.decorators import agent
from utils.executor import execute_plan
from tools import rag_tools

@agent("rag")
async def rag_agent(prompt, memory_log):
    toolset = rag_tools.agent_tools["rag"]
    tool_list = "\n".join([f"{name}: {fn.__doc__.strip()}" for name, fn in toolset.items()])
    system_msg = (
        "You are a Knowledge Retrieval agent. You can only retrieve information from a vector database.\n"
        "You CANNOT add or modify the database.\n"
        f"Tools:\n{tool_list}\n\n"
        "Plan a tool call like:\n"
        '[{"tool": "search_vector_db", "args": ["What is the sun?"]}]'
    )
    return await execute_plan(prompt, agent="rag", system_msg=system_msg)
