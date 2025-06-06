import tools.math_tools
import tools.string_tools
import tools.rag_tools

# Now import agents
from agents import math_agent, string_agent, rag_agent, memory_agent, planner_agent

import asyncio
import json
from agents.planner_agent import planner_agent
from agents import math_agent, string_agent, rag_agent, memory_agent

memory_log = []

agent_registry = {
    "planner": planner_agent,
    "math": math_agent.math_agent,
    "string": string_agent.string_agent,
    "rag": rag_agent.rag_agent,
    "memory": memory_agent.memory_agent,
}

async def multi_agent_router(prompt):
    plan = await planner_agent(prompt, memory_log)
    agent_name = plan.get("agent")
    task = plan.get("task")

    if agent_name not in agent_registry:
        return {"error": f"Unknown agent: {agent_name}"}

    result = await agent_registry[agent_name](task, memory_log)

    if agent_name != "planner" and isinstance(result, dict) and "result" in result:
        memory_log.append((prompt, result["result"]))

    return result

async def main():
    while True:
        prompt = input("\nAsk something (or type 'exit'): ")
        if prompt.lower() == "exit":
            break
        result = await multi_agent_router(prompt)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
