from dataclasses import dataclass

from loguru import logger
from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_random

from dream_factory_evals.df_agent import (
    MarkdownResponse,
    Query,
    TaskConfig,
    ToolCall,
    ToolCallResult,
    setup_task_and_agent,
)


@dataclass
class ChatResult:
    result: str
    tool_calls: dict[str, dict[str, ToolCall | ToolCallResult]]
    message_history: list[ModelMessage] | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


async def chat(
    user_prompt: str, task_config: TaskConfig, message_history: list[ModelMessage] | None = None
) -> ChatResult:
    inputs = Query(query=user_prompt, output_type=MarkdownResponse)
    task_config.new = True
    task, agent = setup_task_and_agent(query=inputs, config=task_config)
    tool_calls: dict[str, dict[str, ToolCall | ToolCallResult]] = {}
    try:
        async for attempt in AsyncRetrying(wait=wait_random(min=1, max=3), stop=stop_after_attempt(3)):
            with attempt:
                async with agent.run_mcp_servers():
                    num_tool_calls = 0
                    async with agent.iter(
                        user_prompt=task.prompt,
                        output_type=inputs.output_type,
                        message_history=message_history,
                    ) as agent_run:
                        async for node in agent_run:
                            if agent.is_call_tools_node(node):
                                for part in node.model_response.parts:
                                    if isinstance(part, ToolCallPart) and part.tool_name not in [
                                        "final_result",
                                    ]:
                                        if num_tool_calls < task_config.max_tool_calls:
                                            tool_calls[part.tool_call_id] = {
                                                "call": ToolCall(
                                                    tool_name=part.tool_name,
                                                    params=part.args_as_dict(),
                                                )
                                            }
                                            num_tool_calls += 1
                                        else:
                                            logger.warning(
                                                f"Too many tool calls: {num_tool_calls} > {task_config.max_tool_calls}"
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
                                            tool_name=part.tool_name,
                                            result=part.content.content,
                                        )
                    res = (
                        agent_run.result.output.content
                        if agent_run.result is not None
                        else "Sorry, I couldn't complete the task."
                    )
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
    return ChatResult(
        result="Sorry, I couldn't complete the task.",
        tool_calls=tool_calls,
        message_history=message_history,
    )
