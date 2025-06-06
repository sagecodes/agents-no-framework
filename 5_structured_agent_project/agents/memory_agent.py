# agents/memory_agent.py

from utils.decorators import agent

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
