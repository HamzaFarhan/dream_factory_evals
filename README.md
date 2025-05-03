MCP Server is in `src/dream_factory_evals/df_mcp.py`

## MCP Tools

Below are the available MCP tools from `src/dream_factory_evals/df_mcp.py`:

```python
@server.tool()
def get_table_records(
    table_name: str,
    filter: str = "",
    fields: str | list[str] = "*",
    limit: int | None = None,
    offset: int = 0,
    order_field: str = "",
    related: str | list[str] = "",
) -> dict:
    """
    Get the records of a table.

    Args:
        table_name: The name of the table to get the records from.
        filter: The filter to apply to the data. This is equivalent to the WHERE clause of a SQL statement.
        fields: The fields to return. If *, all fields will be returned. Defaults to *.
        limit: Max number of records to return. If None, all matching records will be returned, subject to the offset parameter or system settings maximum. Defaults to None.
        offset: Index of first record to return. For example, to get records 91-100, set offset to 90 and limit to 10. Defaults to 0.
        order_field: The field to order the records by. Also supports sort direction ASC or DESC such as 'Name ASC'. Default direction is ASC.
        related: Names of related tables to join via foreign keys based on the schema (e.g. hr_employees_by_department_id). Can be a single table name as string, a list of table names, or '*' to include all related tables. Defaults to None.

    Returns:
        The records of the table.

    Filter Strings:
        Supports standardized ANSI SQL syntax with the following operators:

        Logical Operators (clauses must be wrapped in parentheses):
        - AND: True if both conditions are true
        - OR: True if either condition is true
        - NOT: True if the condition is false

        Comparison Operators:
        - '=' or 'EQ': Equality test
        - '!=' or 'NE' or '<>': Inequality test
        - '>' or 'GT': Greater than
        - '>=' or 'GTE': Greater than or equal
        - '<' or 'LT': Less than
        - '<=' or 'LTE': Less than or equal
        - 'IN': Equality check against values in a set, e.g., a IN (1,2,3)
        - 'NOT IN' or 'NIN': Inverse of IN (MongoDB only)
        - 'LIKE': Pattern matching with '%' wildcard
        - 'CONTAINS': Same as LIKE '%value%'
        - 'STARTS WITH': Same as LIKE 'value%'
        - 'ENDS WITH': Same as LIKE '%value'

        REMINDER: When using an operator, you must include the parentheses.

        Examples:
        - (first_name='John') AND (last_name='Smith')
        - (first_name='John') OR (first_name='Jane')
        - first_name!='John'
        - first_name like 'J%'
        - email like '%@mycompany.com'
        - (Age >= 30) AND (Age < 40)
    """
```

```python
@server.tool()
def get_table_records_by_ids(
    table_name: str, ids: str | list[str], fields: str | list[str] = "*", related: str | list[str] = ""
) -> dict:
    """Get one or more records from a table by their IDs.

    Args:
        table_name: The name of the table to get the records from.
        ids: The IDs of the records to get.
        fields: The fields to return. If *, all fields will be returned. Defaults to *.
        related: Names of related tables to join via foreign keys based on the schema (e.g. hr_employees_by_department_id). Can be a single table name as string, a list of table names, or '*' to include all related tables. Defaults to None.

    Returns:
        The records of the table.
    """
```

```python
@server.tool()
def calculate_sum(values: list[float]) -> float:
    """Calculate the sum of a list of values."""
```

```python
@server.tool()
def calculate_difference(num1: float, num2: float) -> float:
    """Calculate the difference between two numbers by subtracting `num1` from `num2`"""
```

```python
@server.tool()
def calculate_mean(values: list[float]) -> float:
    """Calculate the mean of a list of values."""
```

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

