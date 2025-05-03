import os

import httpx
from loguru import logger
from mcp.server.fastmcp import FastMCP

server = FastMCP(name="dream_factory_mcp")


def get_params(
    filter: str = "",
    fields: str | list[str] = "*",
    limit: int | None = None,
    offset: int = 0,
    order_field: str = "",
    related: str | list[str] = "",
) -> dict:
    params = {}
    if filter:
        params["filter"] = filter
    if fields:
        params["fields"] = fields if isinstance(fields, str) else ",".join(fields)
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset
    if order_field:
        params["order"] = order_field
    if related:
        params["related"] = related if isinstance(related, str) else ",".join(related)
    return params


def table_url_with_headers(
    table_name: str,
    base_url: str | None = None,
    dream_factory_api_key: str | None = None,
) -> dict:
    base_url = base_url or os.environ["DREAM_FACTORY_BASE_URL"]
    dream_factory_api_key = dream_factory_api_key or os.environ["DREAM_FACTORY_API_KEY"]
    return dict(url=f"{base_url}/_table/{table_name}", headers={"X-DreamFactory-API-Key": dream_factory_api_key})


def list_table_names(
    base_url: str | None = None, dream_factory_api_key: str | None = None
) -> dict[str, list[dict[str, str]]]:
    """List the names of all tables in the database.

    Returns:
        A list of table names.
    """
    base_url = base_url or os.environ["DREAM_FACTORY_BASE_URL"]
    dream_factory_api_key = dream_factory_api_key or os.environ["DREAM_FACTORY_API_KEY"]
    return httpx.get(url=f"{base_url}/_table", headers={"X-DreamFactory-API-Key": dream_factory_api_key}).json()


@server.tool()
def get_table_schema(
    table_name: str, base_url: str | None = None, dream_factory_api_key: str | None = None
) -> dict:
    """Get the schema of a table.

    Args:
        table_name: The name of the table.

    Returns:
        The schema of the table.
    """
    base_url = base_url or os.environ["DREAM_FACTORY_BASE_URL"]
    dream_factory_api_key = dream_factory_api_key or os.environ["DREAM_FACTORY_API_KEY"]
    logger.info(f"Accessing schema for table {table_name} with API key {dream_factory_api_key}")
    return httpx.get(
        url=f"{base_url}/_schema/{table_name}", headers={"X-DreamFactory-API-Key": dream_factory_api_key}
    ).json()


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
    """Get the records of a table.

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
    return httpx.get(
        **table_url_with_headers(table_name=table_name),
        params=get_params(
            filter=filter, fields=fields, limit=limit, offset=offset, order_field=order_field, related=related
        ),
    ).json()


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
    params = {"ids": ids if isinstance(ids, str) else ",".join(ids)}
    params.update(get_params(fields=fields, related=related))
    return httpx.get(**table_url_with_headers(table_name=table_name), params=params).json()


@server.tool()
def calculate_sum(values: list[float]) -> float:
    """Calculate the sum of a list of values."""
    return sum(values)


@server.tool()
def calculate_difference(num1: float, num2: float) -> float:
    """Calculate the difference between two numbers by subtracting `num1` from `num2`"""
    return num2 - num1


@server.tool()
def calculate_mean(values: list[float]) -> float:
    """Calculate the mean of a list of values."""
    return sum(values) / len(values)


if __name__ == "__main__":
    server.run()
