from __future__ import annotations

import argparse

import logfire
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    Role,
    ToolCall,
    evaluate,
)

from .output_types import (
    Expense,
    Expenses,
    ProductCount,
    RevenueAmount,
    TotalAmount,
    TotalRevenue,
)

_ = logfire.configure()


finance_dataset = Dataset[Query, QueryResult](
    cases=[
        Case(
            name="finance_l1_q1",
            inputs=Query(query="What was the total revenue in Q4 2022?", output_type=TotalRevenue),
            expected_output=QueryResult(
                result=TotalRevenue(total_revenue=8000),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(quarter=4) AND (year=2022)",
                            "fields": "revenue_amount",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l1_q2",
            inputs=Query(query="How many products are in the Electronics category?", output_type=ProductCount),
            expected_output=QueryResult(
                result=ProductCount(product_count=7),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_products",
                            "filter": "category='Electronics'",
                            "fields": "product_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l1_q3",
            inputs=Query(
                query="What is the total amount spent on Capital expenses in 2022?", output_type=TotalAmount
            ),
            expected_output=QueryResult(
                result=TotalAmount(total_amount=1700),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(category='Capital') AND (expense_date >= '2022-01-01') AND (expense_date <= '2022-12-31')",
                            "fields": "amount",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l1_q4",
            inputs=Query(query="What was the revenue amount for Product 10?", output_type=RevenueAmount),
            expected_output=QueryResult(
                result=RevenueAmount(revenue_amount=1500),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "product_id=10",
                            "fields": "revenue_amount",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l1_q5",
            inputs=Query(query="What are the top 3 highest expenses in 2023?", output_type=Expenses),
            expected_output=QueryResult(
                result=Expenses(
                    expenses=[
                        Expense(
                            expense_id=19,
                            description="Expense 19: Event Sponsorship",
                            amount=1000,
                        ),
                        Expense(
                            expense_id=18,
                            description="Expense 18: Software Upgrade",
                            amount=900,
                        ),
                        Expense(
                            expense_id=17,
                            description="Expense 17: Travel",
                            amount=700,
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(expense_date >= '2023-01-01') AND (expense_date <= '2023-12-31')",
                            "order_field": "amount DESC",
                            "limit": 3,
                        },
                    )
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult(), EvaluateToolCalls()],
)


def main():
    parser = argparse.ArgumentParser(description="Run FINANCE evaluations")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name to evaluate. Examples:\n"
        "  OpenAI: 'openai:gpt-4-turbo', 'openai:gpt-4o'\n"
        "  Anthropic: 'anthropic:claude-3-5-sonnet-latest', 'anthropic:claude-3-opus-latest'\n"
        "  Google: 'google-gla:gemini-1.5-pro', 'google-gla:gemini-1.5-flash'",
    )
    args = parser.parse_args()

    evaluate(model=args.model, dataset=finance_dataset, user_role=Role.FINANCE, level=1)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    for model in models:
        evaluate(model=model, dataset=finance_dataset, user_role=Role.FINANCE, level=1)
