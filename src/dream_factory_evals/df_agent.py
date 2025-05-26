import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Generic, Literal, TypeVar, get_args

from dotenv import load_dotenv
from loguru import logger
from pydantic import AfterValidator, BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer, MCPServerStdio
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.models import KnownModelName, Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_evals import Dataset
from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext
from tenacity import AsyncRetrying, stop_after_attempt, wait_random

from dream_factory_evals.df_mcp import list_table_names

_ = load_dotenv()

MODULE_DIR = Path(__file__).parent

RETRIES = 3
MAX_TOOL_CALLS = 20
STRINGS_SIMILARITY_MODEL = "google-gla:gemini-2.0-flash"

type ModelT = KnownModelName | Literal["SG_LANG", "Qwen2.5"]


def is_known_model_name(model: ModelT) -> bool:
    """Check if the given string is a valid KnownModelName."""
    known_model_names = get_args(KnownModelName.__value__)
    return model in known_model_names


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


InputsT = TypeVar("InputsT")
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
    result: ResultT | None
    tool_calls: list[ToolCall]
    error: str | None = None


class MarkdownResponse(BaseModel):
    content: str


@dataclass
class EvaluateResult(Evaluator[Query[ResultT], QueryResult[ResultT]]):
    def evaluate(self, ctx: EvaluatorContext[Query[ResultT], QueryResult[ResultT]]) -> bool:
        if ctx.expected_output is None:
            return True
        if ctx.output.error is not None:
            return False
        return ctx.output.result == ctx.expected_output.result


@dataclass
class EvaluateToolCalls(Evaluator[Query[ResultT], QueryResult[ResultT]]):
    def evaluate(self, ctx: EvaluatorContext[Query[ResultT], QueryResult[ResultT]]) -> EvaluationReason:
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


class Task(BaseModel, Generic[ResultT]):
    query: Query[ResultT]
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


class TaskConfig(BaseModel):
    user_role: Role
    model: ModelT
    retries: int = RETRIES
    prompt_name: str = "basic_prompt.txt"
    mcp_servers: list[MCPServer] | None = None
    max_tool_calls: int = MAX_TOOL_CALLS
    new: bool = False


def setup_task_and_agent(query: Query[ResultT], config: TaskConfig) -> tuple[Task[ResultT], Agent]:
    available_tables = [
        t["name"]
        for t in list_table_names(
            base_url=os.environ["DREAM_FACTORY_BASE_URL"],
            dream_factory_api_key=os.environ["DREAM_FACTORY_CEO_API_KEY"],
        )["resource"]
    ]

    if config.user_role != Role.CEO:
        available_tables = [t for t in available_tables if t.startswith(config.user_role.value)]

    task = Task(query=query, user_role=config.user_role, available_tables=available_tables)
    url_key = "DREAM_FACTORY_BASE_URL" if not config.new else "NEW_DREAM_FACTORY_BASE_URL"
    api_key_key = (
        f"DREAM_FACTORY_{config.user_role.upper()}_API_KEY"
        if not config.new
        else f"NEW_DREAM_FACTORY_{config.user_role.upper()}_API_KEY"
    )
    tables_mcp_server = MCPServerStdio(
        command="uv",
        args=["run", str(MODULE_DIR / "df_mcp.py")],
        env={"DREAM_FACTORY_BASE_URL": os.environ[url_key], "DREAM_FACTORY_API_KEY": os.environ[api_key_key]},
    )
    agent = Agent(
        model=sglang_model(os.environ["SG_LANG_BASE_URL"])
        if not is_known_model_name(config.model)
        else config.model,
        name="df_agent",
        system_prompt=(MODULE_DIR / config.prompt_name).read_text(),
        mcp_servers=(config.mcp_servers or []) + [tables_mcp_server],
        instrument=True,
        retries=config.retries,
    )
    return task, agent


async def task(inputs: Query[ResultT], config: TaskConfig) -> QueryResult[ResultT]:
    task, agent = setup_task_and_agent(query=inputs, config=config)
    tool_calls: list[ToolCall] = []
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
                                        if num_tool_calls < config.max_tool_calls:
                                            tool_calls.append(
                                                ToolCall(tool_name=part.tool_name, params=part.args_as_dict())
                                            )
                                            num_tool_calls += 1
                                        else:
                                            error_msg = (
                                                f"Too many tool calls: {num_tool_calls} > {config.max_tool_calls}"
                                            )
                                            logger.warning(error_msg)
                                            return QueryResult(result=None, tool_calls=tool_calls, error=error_msg)
                    if agent_run.result is None:
                        return QueryResult(result=None, tool_calls=tool_calls, error="No result produced")
                    return QueryResult(result=agent_run.result.output, tool_calls=tool_calls)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.exception(error_msg)
        return QueryResult(result=None, tool_calls=tool_calls, error=error_msg)
    logger.error(
        (
            "Internal Error: The 'task' function in df_agent.py reached an unexpected state "
            "where it did not explicitly return a QueryResult. This may indicate an issue "
            "with the retry logic or an unhandled execution path."
        )
    )
    return QueryResult(
        result=None, tool_calls=tool_calls, error="Internal Server Error: Unexpected execution path."
    )


def sglang_model(base_url: str) -> Model:
    return OpenAIModel("Qwen2.5", provider=OpenAIProvider(base_url=base_url, api_key="SG_LANG"))


class ReportInfo(BaseModel):
    name: Annotated[str, AfterValidator(lambda x: x.replace(" ", "-").replace(":", "-"))]
    model: ModelT
    user_role: Role
    level: int


def evaluate(
    report_info: ReportInfo,
    dataset: Dataset[Query[ResultT], QueryResult[ResultT]],
    task_config: TaskConfig,
    # task: Callable[[Query[ResultT], TaskConfig], Awaitable[QueryResult[ResultT]]] = task,
):
    logger.info(f"Evaluating {report_info.name}")
    report = dataset.evaluate_sync(task=lambda inputs: task(inputs, task_config), name=report_info.name)
    report.print(
        include_input=True,
        include_output=True,
        include_expected_output=True,
        include_durations=True,
        include_total_duration=True,
        include_averages=True,
    )


def are_strings_similar(str1: str, str2: str, model: ModelT = STRINGS_SIMILARITY_MODEL) -> bool:
    strings_similarity_agent = Agent(model=model, name="strings_similarity_agent", output_type=bool)
    prompt = (
        "The wording/structure/grammar may be different, but are these 2 strings saying the same thing?\n"
        f"String 1: {str1}\n"
        f"String 2: {str2}\n"
    )
    return strings_similarity_agent.run_sync(prompt).output
