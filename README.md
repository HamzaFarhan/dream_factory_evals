# Overview

We are evaluating how an `Agent` uses the `DreamFactory` `MCP`.

Given a query, we evaluate:

1. The actual output
2. The tool calls:
    - The number of tool calls
    - The parameters of the tool calls
3. The duration
4. The cost

## Tables

We have 8 tables in our database:

1. `hr_employees`
2. `hr_departments`
3. `hr_policies`
4. `finance_expenses`
5. `finance_products`
6. `finance_revenues`
7. `ops_machines`
8. `ops_maintenance`

## Roles

We have 4 roles:

1. `CEO`
2. `HR`
3. `Finance`
4. `Ops`

Each role has its own API key.

`CEO` has access to all tables.  
`HR` has access to `hr_employees`, `hr_departments`, `hr_policies`.  
`Finance` has access to `finance_expenses`, `finance_products`, `finance_revenues`.  
`Ops` has access to `ops_machines`, `ops_maintenance`.  

# Implementation

## 1. MCP

The server is configured using `DREAM_FACTORY_BASE_URL` and `DREAM_FACTORY_API_KEY` environment variables.

### Tools

- `get_table_schema`
- `get_table_records`
- `get_table_records_by_ids`
- `calculate_sum`
- `calculate_difference`
- `calculate_mean`

### RBAC

`get_table_schema`, `get_table_records`, and `get_table_records_by_ids` accept `table_name` as a parameter.

If a server configured with a certain role's API key tries to access a table that the role does not have access to, the server will return an error.  
So `RBAC` is already enforced, but the `Agent` needs to know which tables are available to it.  
Ideally, the `MCP` would also have a `list_table_names` tool that returns the tables that the role has access to.
But that tool only worked with the `CEO` API key.

As a workaround, we do this for every `Agent` run:
1. Call the `list_table_names` tool with the `CEO` API key.
2. Drop all tables who's name doesn't start with the role's name.  
   So if the role is `HR`, we drop all tables who's name doesn't start with `hr_`.
3. Append the remaining tables to the `Agent`'s instructions/system prompt along with the role.

## 2. Evals

We have 4 levels of evals with increasing complexity. For each level, we have 3-5 queries per role.  
The queries are not that important because we are working with dummy data. The important thing is the process of creating the queries.

### Structure

Each query has:
- `query_id`
- `query`
- `expected_response`
- `expected_tool_calls`

#### expected_response

This could be anything. The plain string, an object, a list of objects, etc.

A level 1 query's `expected_response` may just be a number:

```json
{
    "query_id": "hr_l1_1",
    "query": "How many employees are there?",
    "expected_response": {
        "number_of_employees": 100
    }
}
```

A level 4 query's `expected_response` may be an object with multiple fields along with analysis:

```json
{
    "query_id": "finance_l4_1",
    "query": "Compare Q4 2023 vs Q4 2024 revenue performance for 'Software' and 'Electronics' products. Calculate growth rates and identify which category performed better. Also analyze total 'Marketing' expenses for both quarters. Provide one strategic recommendation based on the revenue-to-marketing spend efficiency.",
    "expected_response": {
        "quarterly_comparison": {
            "Software": {
                "Q4_2023_revenue": 15420.33,
                "Q4_2024_revenue": 28750.12,
                "growth_rate_percentage": 86.4
            },
            "Electronics": {
                "Q4_2023_revenue": 13831.28,
                "Q4_2024_revenue": 34569.61,
                "growth_rate_percentage": 149.9
            }
        },
        "marketing_expenses": {
            "Q4_2023": 2450.75,
            "Q4_2024": 3200.50
        },
        "analysis": {
            "better_performing_category": "Electronics",
            "revenue_to_marketing_efficiency": "Electronics showed 149.9% growth vs 86.4% for Software, while marketing spend increased only 30.6%"
        },
        "strategic_recommendation": "Allocate more marketing budget to Electronics products in Q1 2025, as they demonstrate superior growth response to marketing investment."
    }
}
```
The problem is, when evaluating the `Agent`'s response against the `expected_response`, we do an equality check.  
Since we're working with LLMs, the `Agent`'s response for the above `hr_l1_1` query may be:
- `100.0`
- `"One Hundred"`
- `"There are 100 employees"`
- ...  

All of these are correct responses to the query, but they are not equal to `100`. And will fail the eval.

To solve this, we use `pydantic` to create `output_type`s for each query. So the `hr_l1_1` query is now defined as:

```python
from pydantic import BaseModel
from pydantic_evals import Case

class EmployeeCount(BaseModel):
    number_of_employees: int

case = Case(
    inputs=Query(
        query="How many employees are there?",
        output_type=EmployeeCount
    ),
    expected_output=QueryResult(
        result=EmployeeCount(number_of_employees=100)
    )
)
```
Now, when our `Agent` is run for this `case`, it will be forced to output a `EmployeeCount` object which will have a valid integer as `number_of_employees`.  
Two `EmployeeCount` objects can be checked for equality using `==`.

But what about free form text like `strategic_recommendation` above for the `finance_l4_1` query?  
Even if the `Agent` outputs a valid string with the correct recommendation, it is unlikely to be the exact string word for word as the one in the `expected_response`.

To solve this, we use another small `Agent` to compare the main `Agent`'s output with the `expected_response`.  
All it does is compare the `expected_response` and the `Agent`'s output strings and returns `True` if they are saying the same thing despite different wording/structure/grammar. Otherwise, it returns `False`.

