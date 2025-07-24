import os
from typing import Any, TypedDict

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
) -> dict[str, str | int | None]:
    params: dict[str, str | int | None] = {}
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


class TableUrlWithHeaders(TypedDict):
    url: str
    headers: dict[str, str]


def table_url_with_headers(
    table_name: str, base_url: str | None = None, dream_factory_api_key: str | None = None
) -> TableUrlWithHeaders:
    base_url = base_url or os.environ["DREAM_FACTORY_BASE_URL"]
    dream_factory_api_key = dream_factory_api_key or os.environ["DREAM_FACTORY_API_KEY"]
    return {"url": f"{base_url}/_table/{table_name}", "headers": {"X-DreamFactory-API-Key": dream_factory_api_key}}


def list_table_names(base_url: str | None = None, dream_factory_api_key: str | None = None) -> dict[str, Any]:
    """List the names of all tables in the database.

    Parameters
    ----------
    base_url : str, optional
        Base URL for the DreamFactory API
    dream_factory_api_key : str, optional
        API key for authentication

    Returns
    -------
    dict
        Dictionary containing list of table names and their metadata
    """
    base_url = base_url or os.environ["DREAM_FACTORY_BASE_URL"]
    dream_factory_api_key = dream_factory_api_key or os.environ["DREAM_FACTORY_API_KEY"]
    return httpx.get(url=f"{base_url}/_table", headers={"X-DreamFactory-API-Key": dream_factory_api_key}).json()


@server.tool()
def get_table_schema(
    table_name: str, base_url: str | None = None, dream_factory_api_key: str | None = None
) -> dict[str, Any]:
    """Get the schema of a table.

    Parameters
    ----------
    table_name : str
        The name of the table
    base_url : str, optional
        Base URL for the DreamFactory API
    dream_factory_api_key : str, optional
        API key for authentication

    Returns
    -------
    dict
        The schema of the table
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
) -> dict[str, Any]:
    """Get the records of a table.

    Parameters
    ----------
    table_name : str
        The name of the table to get the records from
    filter : str, optional
        The filter to apply to the data. This is equivalent to the WHERE clause of a SQL statement
    fields : str or list[str], optional
        The fields to return. If *, all fields will be returned. Default is '*'
    limit : int or None, optional
        Max number of records to return. If None, all matching records will be returned,
        subject to the offset parameter or system settings maximum. Default is None
    offset : int, optional
        Index of first record to return. For example, to get records 91-100,
        set offset to 90 and limit to 10. Default is 0
    order_field : str, optional
        The field to order the records by. Also supports sort direction ASC or DESC
        such as 'Name ASC'. Default direction is ASC
    related : str or list[str], optional
        Names of related tables to join via foreign keys based on the schema
        (e.g. hr_employees_by_department_id). Can be a single table name as string,
        a list of table names, or '*' to include all related tables. Default is ''

    Returns
    -------
    dict
        The records of the table

    Notes
    -----
    Filter Strings support standardized ANSI SQL syntax with the following operators:

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

    Examples
    --------
    >>> # Filter by name
    >>> (first_name='John') AND (last_name='Smith')
    >>> # Filter by multiple first names
    >>> (first_name='John') OR (first_name='Jane')
    >>> # Filter by inequality
    >>> first_name!='John'
    >>> # Pattern matching
    >>> first_name like 'J%'
    >>> email like '%@mycompany.com'
    >>> # Range filtering
    >>> (Age >= 30) AND (Age < 40)
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
) -> dict[str, Any]:
    """Get one or more records from a table by their IDs.

    Parameters
    ----------
    table_name : str
        The name of the table to get the records from
    ids : str or list[str]
        The IDs of the records to get
    fields : str or list[str], optional
        The fields to return. If *, all fields will be returned. Default is '*'
    related : str or list[str], optional
        Names of related tables to join via foreign keys based on the schema
        (e.g. hr_employees_by_department_id). Can be a single table name as string,
        a list of table names, or '*' to include all related tables. Default is ''

    Returns
    -------
    dict
        The records of the table
    """
    params: dict[str, str | int | None] = {"ids": ids if isinstance(ids, str) else ",".join(ids)}
    params.update(get_params(fields=fields, related=related))
    return httpx.get(**table_url_with_headers(table_name=table_name), params=params).json()


@server.tool()
def calculate_sum(values: list[float]) -> float:
    """Calculate the sum of a list of values.

    Parameters
    ----------
    values : list[float]
        List of numerical values to sum

    Returns
    -------
    float
        Sum of the input values
    """
    return sum(values)


@server.tool()
def calculate_difference(num1: float, num2: float) -> float:
    """Calculate the difference between two numbers.

    Parameters
    ----------
    num1 : float
        First number
    num2 : float
        Second number

    Returns
    -------
    float
        The result of num2 - num1
    """
    return num2 - num1


@server.tool()
def calculate_mean(values: list[float]) -> float:
    """Calculate the mean of a list of values.

    Parameters
    ----------
    values : list[float]
        List of numerical values

    Returns
    -------
    float
        Arithmetic mean of the input values
    """
    return sum(values) / len(values)


if __name__ == "__main__":
    server.run()
