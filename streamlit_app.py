import asyncio

import streamlit as st
from loguru import logger
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import KnownModelName

from dream_factory_evals.df_agent import Role, ToolCall, ToolCallResult
from dream_factory_evals.df_chat import ChatResult, chat


async def run_chat(
    prompt: str,
    role: Role,
    model: KnownModelName,
    message_history: list[ModelMessage] | None = None,
) -> ChatResult:
    try:
        chat_result = await chat(
            user_prompt=prompt,
            user_role=role,
            model=model,
            message_history=message_history,
        )
        return chat_result
    except Exception as e:
        logger.exception(f"Error during chat: {e}")
        return ChatResult(result=f"Error: {str(e)}", tool_calls={}, message_history=message_history)


def show_tool_calls(tool_calls: dict[str, dict[str, ToolCall | ToolCallResult]]):
    for _, tool_call in tool_calls.items():
        if tool_call.get("call"):
            st.markdown(
                '<span style="color:rgb(77,168,74);font-weight:bold;">Call</span>',
                unsafe_allow_html=True,
            )
            st.code(f"{tool_call['call'].tool_name}", language="json")
            st.code(f"{tool_call['call'].params}", language="json")  # type: ignore
            if tool_call.get("result"):
                st.markdown(
                    '<span style="color:rgb(73,162,207);font-weight:bold;">Result</span>',
                    unsafe_allow_html=True,
                )
                st.code(f"{tool_call['result'].tool_name}", language="json")
                st.code(f"{tool_call['result'].result}", language="json")  # type: ignore


def show_token_counts(input_tokens: int, output_tokens: int, total_tokens: int):
    color = "rgb(255,179,71)"
    st.markdown(
        f'<span style="color:{color};font-weight:bold;">Input Tokens</span>',
        unsafe_allow_html=True,
    )
    st.code(f"{input_tokens}", language="json")
    st.markdown(
        f'<span style="color:{color};font-weight:bold;">Output Tokens</span>',
        unsafe_allow_html=True,
    )
    st.code(f"{output_tokens}", language="json")
    st.markdown(
        f'<span style="color:{color};font-weight:bold;">Total Tokens</span>',
        unsafe_allow_html=True,
    )
    st.code(f"{total_tokens}", language="json")


st.set_page_config(page_title="Dream Factory Chat", layout="wide")

st.title("DreamFactory Chat")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    model: KnownModelName = st.selectbox(
        "Select Model",
        [
            "google-gla:gemini-2.0-flash",
            "anthropic:claude-3-5-sonnet-latest",
            "openai:gpt-4.1-mini",
            "openai:o4-mini",
        ],
        index=0,  # Default to gemini-2.0-flash
    )

    role = st.selectbox(
        "User Role",
        [Role.CEO, Role.HR, Role.FINANCE, Role.OPS],
        format_func=lambda x: x.value.upper(),
    )
    access = "all" if role == Role.CEO else role.value.upper()
    st.info(f"Selected role: {role.value.upper()} with access to {access} tables")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_message_history" not in st.session_state:
    st.session_state.model_message_history = None

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("tool_calls") and message["role"] == "assistant" and message["tool_calls"]:
            with st.expander(f"Tool calls ({len(message['tool_calls'])})"):
                show_tool_calls(message["tool_calls"])

        if message.get("input_tokens") and message.get("output_tokens") and message.get("total_tokens"):
            with st.expander("Token Usage"):
                show_token_counts(
                    message["input_tokens"],
                    message["output_tokens"],
                    message["total_tokens"],
                )

# User input
if prompt := st.chat_input("Ask something..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result_placeholder = st.empty()

            # Run chat function
            chat_result = asyncio.run(
                run_chat(
                    prompt=prompt,
                    role=role,
                    model=model,
                    message_history=st.session_state.model_message_history,
                )
            )

            # Update message history
            st.session_state.model_message_history = chat_result.message_history

            # Display result
            result_placeholder.markdown(chat_result.result)

            # Display tool calls immediately
            if chat_result.tool_calls:
                with st.expander(f"Tool calls ({len(chat_result.tool_calls)})"):
                    show_tool_calls(chat_result.tool_calls)

            if chat_result.input_tokens and chat_result.output_tokens and chat_result.total_tokens:
                with st.expander("Token Usage"):
                    show_token_counts(
                        chat_result.input_tokens,
                        chat_result.output_tokens,
                        chat_result.total_tokens,
                    )

            # Format and store assistant response
            assistant_message = {
                "role": "assistant",
                "content": chat_result.result,
                "tool_calls": chat_result.tool_calls,
                "input_tokens": chat_result.input_tokens,
                "output_tokens": chat_result.output_tokens,
                "total_tokens": chat_result.total_tokens,
            }
            st.session_state.messages.append(assistant_message)

st.sidebar.markdown("---")
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.model_message_history = None
    st.rerun()
