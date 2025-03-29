import os
from enum import StrEnum

import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai import messages as _messages
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from dream_factory_evals.df_mcp import list_table_names

logfire.configure()


class Success(BaseModel):
    success: bool = Field(description="Whether the agent has successfully completed the main task.")
    response_message: str = Field(description="A message to the user about the result of the current/main task.")
    response_data: str = Field(description="The data returned for the current/main task.")


class Role(StrEnum):
    FINANCE = "finance"
    HR = "hr"
    OPS = "ops"
    CEO = "ceo"


class Task(BaseModel):
    main_task: str
    user_role: Role
    available_tables: list[str]
    latest_user_prompt: str = ""

    def __str__(self):
        res = (
            f"<main_task>\n{self.main_task}\n</main_task>\n\n"
            f"<user_role>\n{self.user_role}\n</user_role>\n\n"
            f"<available_tables>\n{'\n'.join(f'- {t}' for t in self.available_tables).strip()}\n</available_tables>"
        )
        if self.latest_user_prompt:
            res += f"\n\n<latest_user_prompt>\n{self.latest_user_prompt}\n</latest_user_prompt>"
        return res.strip()


def setup_task(main_task: str, user_role: Role, latest_user_prompt: str = "") -> tuple[Task, Agent]:
    available_tables = list_table_names(
        base_url=os.environ["DREAM_FACTORY_BASE_URL"],
        dream_factory_api_key=os.environ["DREAM_FACTORY_CEO_API_KEY"],
    )["resource"]

    if user_role != Role.CEO:
        available_tables = [t["name"] for t in available_tables if t["name"].startswith(user_role.value)]

    task = Task(
        main_task=main_task,
        user_role=user_role,
        available_tables=available_tables,
        latest_user_prompt=latest_user_prompt,
    )

    tables_mcp_server = MCPServerStdio(
        command="uv",
        args=["run", "df_mcp.py"],
        env={
            "DREAM_FACTORY_BASE_URL": os.environ["DREAM_FACTORY_BASE_URL"],
            "DREAM_FACTORY_API_KEY": os.environ[f"DREAM_FACTORY_{user_role.upper()}_API_KEY"],
        },
    )

    agent = Agent(
        model="google-gla:gemini-2.0-flash",
        name="df_agent",
        system_prompt=(
            "You will be given a main task by the user.\n"
            "You will also be given the role of the user.\n"
            "The <available_tables> section will list the tables that the user can access based on their role.\n"
            "So given the main task and the <available_tables>, you would have a good idea of which tables to use.\n"
            "But if you think the user's main task would require you to access a table from a different department, you MUST STOP and return 'success' = False and a helpful detailed message to the user including what your plan was and why you can't do it.\n"
            "Then start off by using the 'get_table_schema' tool to get the schema of the needed tables.\n"
            "Only return 'success' if the main task has been completed."
            "You may have to complete smaller tasks to get to the main task.\n"
        ),
        mcp_servers=[tables_mcp_server],
        instrument=True,
    )
    return task, agent


async def do_task(
    main_task: str,
    user_role: Role,
    latest_user_prompt: str = "",
    message_history: list[_messages.ModelMessage] | None = None,
    usage_limits: UsageLimits | None = UsageLimits(request_limit=15),
) -> Success:
    task, agent = setup_task(main_task=main_task, user_role=user_role, latest_user_prompt=latest_user_prompt)
    result = Success(success=False, response_message="", response_data="")
    async with agent.run_mcp_servers():
        while task.latest_user_prompt != "q":
            response = await agent.run(
                user_prompt=str(task),
                result_type=Success,
                message_history=message_history,
                usage_limits=usage_limits,
            )
            result = response.data
            message_history = response.all_messages()
            if result.success:
                return result
            task.latest_user_prompt = input(f"{result.response_message}  (q to quit)> ")
    return result


# res = await do_task(main_task="I want the department name of alice johnson from hr", user_role=Role.HR)
# res.model_dump()
