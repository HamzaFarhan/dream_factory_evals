from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

load_dotenv()

OutputT = TypeVar("OutputT")

type Level = Literal["level1", "level2", "level3", "level4"]


class ReviewResult(BaseModel):
    correct: bool
    reason: str


router_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    name="router_agent",
    output_type=Level,  # type: ignore
    instructions=(
        "Analyze the incoming query and determine its complexity level.\n"
        "Level 1: Simple counting/lookups.\n"
        "Level 2: Joins/filtering.\n"
        "Level 3: Complex calculations/multi-table analysis.\n"
        "Level 4: Strategic analysis/recommendations requiring deep reasoning.\n"
        "Return the level as a string."
    ),
)
level1_agent = Agent(model="google-gla:gemini-2.0-flash", name="level1_agent")
level2_agent = Agent(model="google-gla:gemini-2.0-flash", name="level2_agent")
level3_agent = Agent(model="google-gla:gemini-2.0-flash", name="level3_agent")
level4_agent = Agent(model="google-gla:gemini-2.0-flash", name="level4_agent")
review_agent = Agent(model="google-gla:gemini-2.0-flash", name="review_agent", output_type=ReviewResult)


@dataclass
class GraphState:
    message_history: list[ModelMessage] = field(default_factory=list)


@dataclass
class RouterNode[OutputT](BaseNode[GraphState, None, OutputT]):
    user_prompt: str
    output_type: type[OutputT]

    async def run(
        self,
        ctx: GraphRunContext[GraphState],
    ) -> Level1Node[OutputT] | Level2Node[OutputT] | Level3Node[OutputT] | Level4Node[OutputT]:
        level = (
            await router_agent.run(user_prompt=self.user_prompt, message_history=ctx.state.message_history)
        ).output
        if level == "level1":
            return Level1Node(user_prompt=self.user_prompt, output_type=self.output_type)
        if level == "level2":
            return Level2Node(user_prompt=self.user_prompt, output_type=self.output_type)
        if level == "level3":
            return Level3Node(user_prompt=self.user_prompt, output_type=self.output_type)
        if level == "level4":
            return Level4Node(user_prompt=self.user_prompt, output_type=self.output_type)
        return Level2Node(user_prompt=self.user_prompt, output_type=self.output_type)


@dataclass
class ReviewNode(BaseNode[GraphState, None, OutputT]):
    user_prompt: str
    output_type: type[OutputT]
    node_output: OutputT
    from_level: Level

    async def run(
        self, ctx: GraphRunContext[GraphState]
    ) -> Level1Node[OutputT] | Level2Node[OutputT] | Level3Node[OutputT] | Level4Node[OutputT] | End[OutputT]:
        prompt = (
            f"The user's query is: {self.user_prompt}\n"
            f"The response from the Agent is: {self.node_output}\n"
            "Is the response correct? Return True or False.\n"
            "If False, return the reason why it is incorrect."
        )
        review = await review_agent.run(user_prompt=prompt, message_history=ctx.state.message_history)
        if review.output.correct:
            return End(self.node_output)
        if self.from_level == "level1":
            return Level1Node(user_prompt=review.output.reason, output_type=self.output_type)
        if self.from_level == "level2":
            return Level2Node(user_prompt=review.output.reason, output_type=self.output_type)
        if self.from_level == "level3":
            return Level3Node(user_prompt=review.output.reason, output_type=self.output_type)
        if self.from_level == "level4":
            return Level4Node(user_prompt=review.output.reason, output_type=self.output_type)
        return End(self.node_output)


@dataclass
class Level1Node[OutputT](BaseNode[GraphState]):
    user_prompt: str
    output_type: type[OutputT]

    async def run(self, ctx: GraphRunContext[GraphState]) -> ReviewNode[OutputT]:
        res = await level1_agent.run(
            user_prompt=self.user_prompt, output_type=self.output_type, message_history=ctx.state.message_history
        )
        ctx.state.message_history += res.new_messages()
        return ReviewNode(
            user_prompt=self.user_prompt, output_type=self.output_type, node_output=res.output, from_level="level1"
        )


@dataclass
class Level2Node[OutputT](BaseNode[GraphState]):
    user_prompt: str
    output_type: type[OutputT]

    async def run(self, ctx: GraphRunContext[GraphState]) -> ReviewNode[OutputT]:
        res = await level2_agent.run(
            user_prompt=self.user_prompt, output_type=self.output_type, message_history=ctx.state.message_history
        )
        ctx.state.message_history += res.new_messages()
        return ReviewNode(
            user_prompt=self.user_prompt, output_type=self.output_type, node_output=res.output, from_level="level2"
        )


@dataclass
class Level3Node[OutputT](BaseNode[GraphState]):
    user_prompt: str
    output_type: type[OutputT]

    async def run(self, ctx: GraphRunContext[GraphState]) -> ReviewNode[OutputT]:
        res = await level3_agent.run(
            user_prompt=self.user_prompt, output_type=self.output_type, message_history=ctx.state.message_history
        )
        ctx.state.message_history += res.new_messages()
        return ReviewNode(
            user_prompt=self.user_prompt, output_type=self.output_type, node_output=res.output, from_level="level3"
        )


@dataclass
class Level4Node[OutputT](BaseNode[GraphState]):
    user_prompt: str
    output_type: type[OutputT]

    async def run(self, ctx: GraphRunContext[GraphState]) -> ReviewNode[OutputT]:
        res = await level4_agent.run(
            user_prompt=self.user_prompt, output_type=self.output_type, message_history=ctx.state.message_history
        )
        ctx.state.message_history += res.new_messages()
        return ReviewNode(
            user_prompt=self.user_prompt, output_type=self.output_type, node_output=res.output, from_level="level4"
        )


graph = Graph(nodes=[RouterNode, Level1Node, Level2Node, Level3Node, Level4Node, ReviewNode], name="router_graph")
graph.mermaid_save("router_graph.jpg", direction="TB", highlighted_nodes=[RouterNode, ReviewNode])
