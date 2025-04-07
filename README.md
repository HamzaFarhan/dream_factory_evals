MCP Server is in `src/dream_factory_evals/df_mcp.py`
Queries are in the `levels` directory
Extracted JSON data is in the `data` directory
MCP Client (AI Agent) is in `src/dream_factory_evals/df_agent.py`

The code in `df_agent.py` is straight forward using pydantic-ai but it's not documented.

You can run the agent with some inputs to see how it uses the MCP Server:

1. Install uv: https://docs.astral.sh/uv/getting-started/installation/
2. Clone the repo
3. Have a .env file in the root of the repo that looks like this:

```
DREAM_FACTORY_BASE_URL=
DREAM_FACTORY_CEO_API_KEY= # The all-access one
DREAM_FACTORY_FINANCE_API_KEY=
DREAM_FACTORY_HR_API_KEY=
DREAM_FACTORY_OPS_API_KEY=
GEMINI_API_KEY=
...
```

4. Run the agent:

```bash
cd src/dream_factory_evals
uv run df_agent.py
```

You can also have a look and give feedback on the `query-generation.mdc` cursor rules which is basically the prompt for generating the queries.
