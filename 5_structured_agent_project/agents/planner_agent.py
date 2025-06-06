import json
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from utils.decorators import agent, agent_registry

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@agent("planner")
async def planner_agent(prompt, memory_log):
    context = "\n".join([f"- {q} → {r}" for q, r in memory_log[-5:]]) or "No history."
    available_agents = [a for a in agent_registry if a != "planner"]
    agent_list = "\n".join([f"- {a}" for a in available_agents])

    system_msg = (
        f"You are a routing agent.\nAvailable agents:\n{agent_list}\n\n"
        f"Recent memory:\n{context}\n\n"
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
