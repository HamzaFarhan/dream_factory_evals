import os

import logfire
from pydantic_ai import Agent, RunContext
from pydantic_ai import messages as _messages
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from dream_factory_evals.base_models import Success, Task

env = dict(os.environ)
env["BASE_URL"] = "https://demov7.dreamfactory.com/api/v2/yearlingsolutions"
env["X-DreamFactory-API-Key"] = "fe83a1ba12d241f7d88007cda016be8edbd49eb35ef1a7083fbaac86eb8a1761"

logfire.configure()

tables_mcp_server = MCPServerStdio(command="uv", args=["run", "dream_factory_mcp.py"], env=env)

agent = Agent(
    model="google-gla:gemini-2.0-flash",
    name="level_1_agent",
    system_prompt=(
        "Only return 'success' if the main task has been completed."
        "You may have to complete smaller tasks to get to the main task."
    ),
    deps_type=Task,
    mcp_servers=[tables_mcp_server],
    instrument=True,
)


@agent.system_prompt
async def system_prompt(ctx: RunContext[Task]) -> str:
    return f"<main_task>\n{ctx.deps.main_task}\n</main_task>"


async def run_agent(user_prompt: str, message_history: list[_messages.ModelMessage] | None = None) -> Success:
    task = Task(main_task=user_prompt)
    result = Success(success=False, response_message="", response_data="")
    async with agent.run_mcp_servers():
        while True:
            response = await agent.run(
                user_prompt=user_prompt,
                deps=task,
                result_type=Success,
                message_history=message_history,
                usage_limits=UsageLimits(request_limit=5),
            )
            result = response.data
            message_history = response.all_messages()
            if result.success:
                return result
            user_prompt = input(f"{result.response_message}  > ")
