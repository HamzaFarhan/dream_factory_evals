from dataclasses import dataclass
from functools import partial
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.models import KnownModelName
from pydantic_evals import Dataset

ResultT = TypeVar("ResultT")


@dataclass
class Query[ResultT]:
    query: str
    output_type: type[ResultT]


class ToolCall(BaseModel):
    tool_name: str
    params: dict[str, Any]


@dataclass
class QueryResult[ResultT]:
    result: ResultT | None
    tool_calls: list[ToolCall]
    error: str | None = None


async def task(inputs: Query[ResultT], model: KnownModelName, agent_name: str) -> QueryResult[ResultT]:
    agent = Agent(model=model, name=agent_name, instructions="Help the user with their query.")
    tool_calls: list[ToolCall] = []
    async with agent.iter(user_prompt=inputs.query, output_type=inputs.output_type) as agent_run:
        async for node in agent_run:
            if agent.is_call_tools_node(node):
                for part in node.model_response.parts:
                    if isinstance(part, ToolCallPart) and part.tool_name not in ["final_result"]:
                        tool_calls.append(ToolCall(tool_name=part.tool_name, params=part.args_as_dict()))

    if agent_run.result is None:
        return QueryResult(result=None, tool_calls=tool_calls, error="No result from agent")
    return QueryResult(result=agent_run.result.output, tool_calls=tool_calls)


async def evaluate(dataset: Dataset[Query[ResultT], QueryResult[ResultT]], model: KnownModelName, agent_name: str):
    report = await dataset.evaluate(task=partial(task, model=model, agent_name=agent_name))
    report.print(
        include_input=True,
        include_output=True,
        include_expected_output=True,
        include_durations=True,
        include_total_duration=True,
        include_averages=True,
    )
