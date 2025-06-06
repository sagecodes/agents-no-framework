import json
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from utils.logger import Logger
from utils.decorators import agent_tools, tool_registry

logger = Logger()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def execute_plan(user_prompt, agent=None, system_msg=None):
    toolset = agent_tools.get(agent, tool_registry)
    tool_list = "\n".join([f"{name}: {fn.__doc__.strip()}" for name, fn in toolset.items()])
    if not system_msg:
        system_msg = (
            "You are a reasoning agent. Use tools from the list below to accomplish your tasks.\n"
            f"Tools:\n{tool_list}\n\n"
            "For each step, return a list of tool calls like:\n"
            '[\n'
            '  {"tool": "example_tool", "args": [1, 2], "reasoning": "Explain why this tool is called."},\n'
            '  {"tool": "another_tool", "args": ["previous"], "reasoning": "Explain why using the previous result."}\n'
            ']\n'
            'IMPORTANT: Always include a "reasoning" field explaining why this tool is being called.'
        )



    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_plan = response.choices[0].message.content
    print("\n[LLM PLAN]", raw_plan)
    plan = json.loads(raw_plan)

    steps_log = []
    last_result = None

    try:
        for step in plan:
            tool_name = step["tool"]
            args = step["args"]
            reasoning = step.get("reasoning", "")
            args = [last_result if str(a).lower() == "previous" else a for a in args]

            if tool_name in toolset:
                result = toolset[tool_name](*args)
            else:
                await logger.log(tool=tool_name, args=args, error="Unknown tool", reasoning=reasoning)
                raise ValueError(f"Unknown tool: {tool_name}")

            await logger.log(tool=tool_name, args=args, result=result, reasoning=reasoning)
            steps_log.append({"tool": tool_name, "args": args, "result": result, "reasoning": reasoning})
            last_result = result

        return {"final_result": last_result, "steps": steps_log}

    except Exception as e:
        await logger.log(tool=tool_name if "tool_name" in locals() else "unknown", args=args if "args" in locals() else [], error=str(e))
        return {"error": str(e), "steps": steps_log}
