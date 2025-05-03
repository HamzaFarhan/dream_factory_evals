from pydantic_ai import Agent

agent = Agent(model="openai:o4-mini", name="test_agent")

res = await agent.run("what is 1000/54?")
res.
