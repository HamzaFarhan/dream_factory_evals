import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from dream_factory_evals.df_mcp import list_table_names

MODULE_DIR = Path(__file__).parent


@dataclass
class Deps:
    active_project: str


def get_current_time() -> str:
    return f"<current_time>\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n</current_time>"


def get_available_tables() -> str:
    available_tables = [
        t["name"]
        for t in list_table_names(
            base_url=os.environ["DREAM_FACTORY_BASE_URL"],
            dream_factory_api_key=os.environ["DREAM_FACTORY_CEO_API_KEY"],
        )["resource"]
    ]
    return f"<available_tables>\n{json.dumps(available_tables)}\n</available_tables>"


tables_mcp_server = MCPServerStdio(
    command="uv",
    args=["run", str(MODULE_DIR / "src/dream_factory_evals/df_mcp.py")],
    env={
        "DREAM_FACTORY_BASE_URL": os.environ["DREAM_FACTORY_BASE_URL"],
        "DREAM_FACTORY_API_KEY": os.environ["DREAM_FACTORY_CEO_API_KEY"],
    },
)
thinking_server = MCPServerStdio(command="npx", args=["-y", "@modelcontextprotocol/server-sequential-thinking"])
agent = Agent(
    model="google-gla:gemini-2.0-flash",
    instructions=[
        "You are a helpful assistant that can answer questions and help with tasks.",
        get_current_time,
        get_available_tables,
    ],
    deps_type=Deps,
    mcp_servers=[thinking_server, tables_mcp_server],
)


deps = Deps(active_project="Gary's Project")


async def main():
    async with agent.run_mcp_servers():
        res = await agent.run(user_prompt="how many total employees are there? Use the thinking tool.", deps=deps)
        print(res.output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
