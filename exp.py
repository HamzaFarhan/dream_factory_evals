from dataclasses import dataclass
from datetime import datetime

from pydantic_ai import Agent, RunContext


@dataclass
class Deps:
    active_project: str


def get_current_time() -> str:
    return f"<current_time>\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n</current_time>"


def get_active_project(ctx: RunContext[Deps]) -> str:
    return f"<active_project>\n{ctx.deps.active_project}\n</active_project>"


agent = Agent(
    model="google-gla:gemini-2.0-flash",
    instructions=[
        "You are a helpful assistant that can answer questions and help with tasks.",
        get_current_time,
        get_active_project,
    ],
    deps_type=Deps,
)


deps = Deps(active_project="Gary's Project")
res = agent.run_sync(user_prompt="What is the current active project?", deps=deps)
print(res.all_messages())
