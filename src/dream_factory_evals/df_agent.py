import os
from dataclasses import dataclass
from enum import StrEnum
from functools import partial
from typing import Any, TypeVar

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart
from pydantic_ai.models import KnownModelName
from pydantic_evals import Dataset
from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_random

from dream_factory_evals.df_mcp import list_table_names

load_dotenv()

MAX_TOOL_CALLS = 50
STRINGS_SIMILARITY_MODEL = "google-gla:gemini-1.5-flash"


class ToolCall(BaseModel):
    tool_name: str
    params: dict[str, Any]


class ToolCallResult(BaseModel):
    tool_name: str
    result: Any


class CantAccessTable(BaseModel):
    reason: str


class Role(StrEnum):
    FINANCE = "finance"
    HR = "hr"
    OPS = "ops"
    CEO = "ceo"


ResultT = TypeVar("ResultT")


@dataclass
class Query[ResultT]:
    query: str
    output_type: type[ResultT]
    result_schema: str = ""

    @property
    def prompt(self) -> str:
        res = f"<query>\n{self.query}\n</query>"
        if self.result_schema:
            res += f"\n\n<result_schema>\n{self.result_schema}\n</result_schema>"
        return res


@dataclass
class QueryResult[ResultT]:
    result: ResultT
    tool_calls: list[ToolCall]


@dataclass
class ChatResult:
    result: str
    tool_calls: dict[str, dict[str, ToolCall | ToolCallResult]]
    message_history: list[ModelMessage] | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class EvaluateResult(Evaluator[Query, QueryResult]):
    def evaluate(self, ctx: EvaluatorContext[Query, QueryResult]) -> bool:
        if ctx.expected_output is None:
            return True
        return ctx.output.result == ctx.expected_output.result


@dataclass
class EvaluateToolCalls(Evaluator[Query, QueryResult]):
    def evaluate(self, ctx: EvaluatorContext[Query, QueryResult]) -> EvaluationReason:
        if ctx.expected_output is None:
            return EvaluationReason(value=True)
        if len(ctx.output.tool_calls) > len(ctx.expected_output.tool_calls):
            return EvaluationReason(
                value=False,
                reason=f"Too many tool calls: {len(ctx.output.tool_calls)} > {len(ctx.expected_output.tool_calls)}",
            )
        reason = ""
        tool_num = 1
        for output_tool_call, expected_tool_call in zip(ctx.output.tool_calls, ctx.expected_output.tool_calls):
            if output_tool_call.tool_name != expected_tool_call.tool_name:
                reason += f"Tool call mismatch: {output_tool_call.tool_name} != {expected_tool_call.tool_name} at tool number: {tool_num}\n"
            if sorted(output_tool_call.params) != sorted(expected_tool_call.params):
                reason += f"Tool call params mismatch: {output_tool_call.params} != {expected_tool_call.params} at tool number: {tool_num}\n"
            tool_num += 1
        if reason:
            return EvaluationReason(value=False, reason=reason)
        return EvaluationReason(value=True)


class Task(BaseModel):
    query: Query
    user_role: Role
    available_tables: list[str]

    @property
    def prompt(self) -> str:
        res = (
            f"<main_task>\n{self.query.prompt}\n</main_task>\n\n"
            f"<user_role>\n{self.user_role}\n</user_role>\n\n"
            f"<available_tables>\n{'\n'.join(f'- {t}' for t in self.available_tables).strip()}\n</available_tables>"
        )
        return res.strip()


def setup_task_and_agent(
    query: Query[ResultT], user_role: Role, model: KnownModelName, new: bool = False
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

    task = Task(query=query, user_role=user_role, available_tables=available_tables)
    url_key = "DREAM_FACTORY_BASE_URL" if not new else "NEW_DREAM_FACTORY_BASE_URL"
    api_key_key = (
        f"DREAM_FACTORY_{user_role.upper()}_API_KEY"
        if not new
        else f"NEW_DREAM_FACTORY_{user_role.upper()}_API_KEY"
    )
    tables_mcp_server = MCPServerStdio(
        command="uv",
        args=["run", "src/dream_factory_evals/df_mcp.py"],
        env={"DREAM_FACTORY_BASE_URL": os.environ[url_key], "DREAM_FACTORY_API_KEY": os.environ[api_key_key]},
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
            "Sometimes, trying different string cases (e.g. 'Active' vs 'active') may help.\n"
            "Efficient tool use is encouraged. So if you think you can do something in fewer tool calls, "
            "for example, using 'related' to join tables instead of calling 'get_table_records' multiple times, "
            "then do so."
        ),
        mcp_servers=[tables_mcp_server],
        instrument=True,
        retries=3,
    )
    return task, agent


async def task(
    inputs: Query,
    user_role: Role,
    model: KnownModelName,
    max_tool_calls: int = MAX_TOOL_CALLS,
) -> QueryResult:
    task, agent = setup_task_and_agent(query=inputs, user_role=user_role, model=model)
    tool_calls = []
    try:
        async for attempt in AsyncRetrying(wait=wait_random(min=1, max=3), stop=stop_after_attempt(3)):
            with attempt:
                async with agent.run_mcp_servers():
                    num_tool_calls = 0
                    async with agent.iter(user_prompt=task.prompt, output_type=inputs.output_type) as agent_run:
                        async for node in agent_run:
                            if agent.is_call_tools_node(node):
                                for part in node.model_response.parts:
                                    if isinstance(part, ToolCallPart) and part.tool_name not in [
                                        "get_table_schema",
                                        "final_result",
                                    ]:
                                        if num_tool_calls < max_tool_calls:
                                            tool_calls.append(
                                                ToolCall(tool_name=part.tool_name, params=part.args_as_dict())
                                            )
                                            num_tool_calls += 1
                                        else:
                                            logger.warning(
                                                f"Too many tool calls: {num_tool_calls} > {max_tool_calls}"
                                            )
                                            return QueryResult(result=None, tool_calls=tool_calls)

                    res = agent_run.result.output if agent_run.result is not None else None
                    return QueryResult(result=res, tool_calls=tool_calls)
    except RetryError as e:
        logger.exception(e)
    return QueryResult(result=None, tool_calls=tool_calls)


async def chat(
    user_prompt: str,
    user_role: Role,
    model: KnownModelName,
    message_history: list[ModelMessage] | None = None,
    # usage: Usage | None = None,
    max_tool_calls: int = MAX_TOOL_CALLS,
) -> ChatResult:
    inputs = Query(query=user_prompt, output_type=str)
    task, agent = setup_task_and_agent(query=inputs, user_role=user_role, model=model, new=True)
    tool_calls = {}
    try:
        async for attempt in AsyncRetrying(wait=wait_random(min=1, max=3), stop=stop_after_attempt(3)):
            with attempt:
                async with agent.run_mcp_servers():
                    num_tool_calls = 0
                    async with agent.iter(
                        user_prompt=task.prompt,
                        output_type=inputs.output_type,
                        message_history=message_history,
                        # usage=usage,
                    ) as agent_run:
                        async for node in agent_run:
                            if agent.is_call_tools_node(node):
                                for part in node.model_response.parts:
                                    if isinstance(part, ToolCallPart) and part.tool_name not in [
                                        "final_result",
                                    ]:
                                        if num_tool_calls < max_tool_calls:
                                            tool_calls[part.tool_call_id] = {
                                                "call": ToolCall(
                                                    tool_name=part.tool_name, params=part.args_as_dict()
                                                )
                                            }
                                            num_tool_calls += 1
                                        else:
                                            logger.warning(
                                                f"Too many tool calls: {num_tool_calls} > {max_tool_calls}"
                                            )
                                            usage = agent_run.usage()
                                            return ChatResult(
                                                result="",
                                                tool_calls=tool_calls,
                                                message_history=agent_run.ctx.state.message_history,
                                                input_tokens=usage.request_tokens,
                                                output_tokens=usage.response_tokens,
                                                total_tokens=usage.total_tokens,
                                            )
                            elif agent.is_model_request_node(node):
                                for part in node.request.parts:
                                    if isinstance(part, ToolReturnPart) and part.tool_name not in [
                                        "get_table_schema",
                                        "final_result",
                                    ]:
                                        tool_calls[part.tool_call_id]["result"] = ToolCallResult(
                                            tool_name=part.tool_name, result=part.content.content
                                        )
                    res = agent_run.result.output if agent_run.result is not None else "Sorry, I couldn't complete the task."
                    usage = agent_run.usage()
                    return ChatResult(
                        result=res,
                        tool_calls=tool_calls,
                        message_history=agent_run.ctx.state.message_history,
                        input_tokens=usage.request_tokens,
                        output_tokens=usage.response_tokens,
                        total_tokens=usage.total_tokens,
                    )
    except RetryError as e:
        logger.exception(e)
    return ChatResult(result="Sorry, I couldn't complete the task.", tool_calls=tool_calls, message_history=message_history)


def evaluate(
    model: KnownModelName,
    dataset: Dataset[Query, QueryResult],
    user_role: Role,
    level: int,
    max_tool_calls: int = MAX_TOOL_CALLS,
):
    name = f"{model.upper()}-{user_role.value.upper()}-LEVEL-{level}"

    report = dataset.evaluate_sync(
        task=partial(task, user_role=user_role, model=model, max_tool_calls=max_tool_calls), name=name
    )
    report.print(
        include_input=True,
        include_output=True,
        include_expected_output=True,
        include_durations=True,
        include_total_duration=True,
        include_averages=True,
    )


def are_strings_similar(str1: str, str2: str, model: KnownModelName = STRINGS_SIMILARITY_MODEL) -> bool:
    strings_similarity_agent = Agent(model=model, name="strings_similarity_agent", output_type=bool)
    prompt = (
        "The wording/structure/grammar may be different, but are these 2 strings saying the same thing?\n"
        f"String 1: {str1}\n"
        f"String 2: {str2}\n"
    )
    return strings_similarity_agent.run_sync(prompt).output


async def main():
    class Email(BaseModel):
        email: str

    inputs = Query(query="What is the email address of Alice Johnson?", output_type=Email)
    user_role = Role.HR
    model = "google-gla:gemini-2.0-flash"
    result = await task(inputs=inputs, user_role=user_role, model=model)
    print(f"\n---\nRESULT:\n\n{result.result}\n\n---\n")
    print(f"TOOL CALLS:\n\n{result.tool_calls}\n---\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
