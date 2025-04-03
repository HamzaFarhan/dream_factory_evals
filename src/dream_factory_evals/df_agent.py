import os
from enum import StrEnum

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models import KnownModelName

from dream_factory_evals.df_mcp import list_table_names

load_dotenv()


class CantAccessTable(BaseModel):
    reason: str


class Role(StrEnum):
    FINANCE = "finance"
    HR = "hr"
    OPS = "ops"
    CEO = "ceo"


class Task(BaseModel):
    main_task: str
    user_role: Role
    available_tables: list[str]

    def __str__(self):
        res = (
            f"<main_task>\n{self.main_task}\n</main_task>\n\n"
            f"<user_role>\n{self.user_role}\n</user_role>\n\n"
            f"<available_tables>\n{'\n'.join(f'- {t}' for t in self.available_tables).strip()}\n</available_tables>"
        )
        return res.strip()


def setup_task_and_agent(
    main_task: str, user_role: Role, model: KnownModelName = "google-gla:gemini-2.0-flash"
) -> tuple[Task, Agent]:
    available_tables = [
        t["name"]
        for t in list_table_names(
            base_url=os.environ["DREAM_FACTORY_BASE_URL"],
            dream_factory_api_key=os.environ["DREAM_FACTORY_CEO_API_KEY"],
        )["resource"]
    ]

    if user_role != Role.CEO:
        available_tables = [t for t in available_tables if t.startswith(user_role.value)]

    task = Task(main_task=main_task, user_role=user_role, available_tables=available_tables)

    tables_mcp_server = MCPServerStdio(
        command="uv",
        args=["run", "/home/hamza/dev/dream_factory_evals/src/dream_factory_evals/df_mcp.py"],
        env={
            "DREAM_FACTORY_BASE_URL": os.environ["DREAM_FACTORY_BASE_URL"],
            "DREAM_FACTORY_API_KEY": os.environ[f"DREAM_FACTORY_{user_role.upper()}_API_KEY"],
        },
    )

    agent = Agent(
        model=model,
        name="df_agent",
        system_prompt=(
            "You will be given a main task by the user.\n"
            "You will also be given the role of the user.\n"
            "The <available_tables> section will list the tables that the user can access based on their role.\n"
            "So given the main task and the <available_tables>, you would have a good idea of which tables to use.\n"
            "But if you think the user's main task would require you to access a table from a different department "
            "(you would be guessing the name of the department and the table), you MUST STOP and return a "
            "CantAccessTable object with a helpful detailed reason to the user including what your plan was and why you can't do it.\n"
            "If you do have access to the needed tables, start off by using the 'get_table_schema' tool to get the schema of the needed tables.\n"
            "Returning anything other than a CantAccessTable object as your final output will be considered a success.\n"
            "So keep calling using your tools until you successfully complete the main task. "
            "You may have to complete smaller tasks to get to the main task.\n"
        ),
        mcp_servers=[tables_mcp_server],
        instrument=True,
    )
    return task, agent
