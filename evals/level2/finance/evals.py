from __future__ import annotations

import argparse
from datetime import date as date_
from functools import partial

from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    Role,
    ToolCall,
    task,
)

from .types import (
    CategoryRevenueComparison,
    ExpenseComparison,
    HardwareRevenue,
    HardwareRevenues,
    ProductRevenueInfo,
    ProfitInfo,
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


FINANCE_RESULT_TYPES = (
    ProductRevenueInfo | CategoryRevenueComparison | ProfitInfo | HardwareRevenues | ExpenseComparison
)

finance_dataset = Dataset[Query, QueryResult](
    cases=[
        Case(
            name="finance_l2_1",
            inputs=Query(
                query="What is the revenue amount for Product 12, and what is its product category?",
                output_type=ProductRevenueInfo,
            ),
            expected_output=QueryResult(
                result=ProductRevenueInfo(product_name="Product 12", revenue_amount=1600, category="Hardware"),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "product_id=12",
                            "fields": ["revenue_amount"],
                            "related": "finance_products_by_product_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l2_2",
            inputs=Query(
                query="Compare the total revenue of Electronics products to Software products in Q2 2022.",
                output_type=CategoryRevenueComparison,
            ),
            expected_output=QueryResult(
                result=CategoryRevenueComparison(electronics_revenue=1500, software_revenue=2800),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(quarter=2) AND (year=2022)",
                            "fields": "revenue_amount",
                            "related": "finance_products_by_product_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l2_3",
            inputs=Query(
                query="What was the profit (revenue minus expenses) for Q3 2022?", output_type=ProfitInfo
            ),
            expected_output=QueryResult(
                result=ProfitInfo(total_revenue=7750, total_expenses=2000, profit=5750),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(quarter=3) AND (year=2022)",
                            "fields": "revenue_amount",
                        },
                    ),
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(expense_date >= '2022-07-01') AND (expense_date <= '2022-09-30')",
                            "fields": "amount",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="finance_l2_4",
            inputs=Query(
                query="List all Hardware products with their revenue in 2022, sorted by revenue amount.",
                output_type=HardwareRevenues,
            ),
            expected_output=QueryResult(
                result=HardwareRevenues(
                    hardware_revenues=[
                        HardwareRevenue(product_name="Product 18", revenue_amount=1900),
                        HardwareRevenue(product_name="Product 15", revenue_amount=1750),
                        HardwareRevenue(product_name="Product 12", revenue_amount=1600),
                        HardwareRevenue(product_name="Product 9", revenue_amount=1450),
                        HardwareRevenue(product_name="Product 6", revenue_amount=1300),
                        HardwareRevenue(product_name="Product 3", revenue_amount=1150),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "finance_products",
                            "filter": "category='Hardware'",
                            "fields": ["name", "product_id"],
                            "related": "finance_revenues_by_product_id",
                            "order_field": "finance_revenues_by_product_id.revenue_amount DESC",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="finance_l2_5",
            inputs=Query(
                query="Compare the expenses for Capital vs Operational categories in the first half of 2022.",
                output_type=ExpenseComparison,
            ),
            expected_output=QueryResult(
                result=ExpenseComparison(capital_expenses=1200, operational_expenses=1050),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(expense_date >= '2022-01-01') AND (expense_date <= '2022-06-30')",
                            "fields": ["amount", "category"],
                        },
                    )
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult(), EvaluateToolCalls()],
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()
    user_role = Role.FINANCE
    name = f"level2_finance_{args.model}"
    report = finance_dataset.evaluate_sync(task=partial(task, user_role=user_role, model=args.model), name=name)
    print(report)


if __name__ == "__main__":
    main()
