from __future__ import annotations

from datetime import date as date_

from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    ReportInfo,
    Role,
    TaskConfig,
    ToolCall,
    evaluate,
)

from .output_types import (
    CategoryRevenueComparison,
    ExpenseComparison,
    HardwareRevenue,
    HardwareRevenues,
    ProductRevenueInfo,
    ProfitInfo,
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = ProductRevenueInfo | CategoryRevenueComparison | ProfitInfo | HardwareRevenues | ExpenseComparison

finance_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
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
                        tool_name="get_table_records",
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
                        tool_name="get_table_records",
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
                query="What was the profit (revenue minus expenses) for Q3 2022?",
                output_type=ProfitInfo,
            ),
            expected_output=QueryResult(
                result=ProfitInfo(total_revenue=7750, total_expenses=2000, profit=5750),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(quarter=3) AND (year=2022)",
                            "fields": "revenue_amount",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
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
                        tool_name="get_table_records",
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
                        tool_name="get_table_records",
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
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)


async def eval_vs_thinking(model: KnownModelName):
    role = Role.CEO
    level = 2
    task_config = TaskConfig(user_role=role, model=model)
    # evaluate(
    #     report_info=ReportInfo(
    #         name=f"{model}-{role.value}-level-{level}", model=model, user_role=role, level=level
    #     ),
    #     dataset=finance_dataset,
    #     task_config=task_config,
    # )
    thinking_server = MCPServerStdio(
        command="npx", args=["-y", "@modelcontextprotocol/server-sequential-thinking"]
    )
    task_config = TaskConfig(user_role=role, model=model, mcp_servers=[thinking_server])
    await evaluate(
        report_info=ReportInfo(
            name=f"{model}-{role.value}-level-{level}-thinking",
            model=model,
            user_role=role,
            level=level,
        ),
        dataset=finance_dataset,
        task_config=task_config,
    )


async def main():
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    for model in models:
        await evaluate(
            report_info=ReportInfo(
                name=f"{model}-{Role.FINANCE.value}-level-2",
                model=model,
                user_role=Role.FINANCE,
                level=2,
            ),
            dataset=finance_dataset,
            task_config=TaskConfig(user_role=Role.FINANCE, model=model),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
