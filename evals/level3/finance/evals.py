from __future__ import annotations

from datetime import date as date_

from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    ToolCall,
)

from .output_types import (
    CategoryTotal,
    CategoryTotals,
    ExpensePercentage,
    Q1Profit,
    QuarterlyAnalysis,
    QuarterlyAnalysisItem,
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = QuarterlyAnalysis | Q1Profit | ExpensePercentage | CategoryTotals

finance_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="finance_l3_1",
            inputs=Query(
                query="Compare the performance of software products against their capital expenses in 2022. For each quarter, show the total software revenue and any capital expenses made in that period, and calculate the return on investment (ROI).",
                output_type=QuarterlyAnalysis,
            ),
            expected_output=QueryResult(
                result=QuarterlyAnalysis(
                    quarterly_analysis=[
                        QuarterlyAnalysisItem(
                            quarter="Q1 2022",
                            software_products=["Product 5", "Product 17"],
                            total_revenue=3100,
                            capital_expenses=0,
                            roi=None,
                            notes="No capital expenses in this quarter",
                        ),
                        QuarterlyAnalysisItem(
                            quarter="Q2 2022",
                            software_products=["Product 2", "Product 14"],
                            total_revenue=2800,
                            capital_expenses=1200,
                            roi=1.33,
                            notes="High capital expenses",
                        ),
                        QuarterlyAnalysisItem(
                            quarter="Q3 2022",
                            software_products=["Product 11"],
                            total_revenue=1550,
                            capital_expenses=0,
                            roi=None,
                            notes="No capital expenses in this quarter",
                        ),
                        QuarterlyAnalysisItem(
                            quarter="Q4 2022",
                            software_products=["Product 8", "Product 20"],
                            total_revenue=3400,
                            capital_expenses=500,
                            roi=5.8,
                            notes="Good ROI with moderate capital investment",
                        ),
                    ],
                    summary="Software product revenues fluctuated throughout 2022, with Q4 showing the highest revenue. Capital expenses were concentrated in Q2 and Q4, with Q4 showing the best ROI. The overall trend shows variable revenue performance with strategic capital investments.",
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_products",
                            "filter": "category='Software'",
                            "related": "finance_revenues_by_product_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(category='Capital') AND (expense_date >= '2022-01-01') AND (expense_date <= '2022-12-31')",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="finance_l3_2",
            inputs=Query(
                query="What was the quarterly profit (revenue minus expenses) for Q1 2022?", output_type=Q1Profit
            ),
            expected_output=QueryResult(
                result=Q1Profit(q1_2022_profit=6500),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(quarter=1) AND (year=2022)",
                            "fields": [
                                "revenue_amount",
                                "revenue_date",
                                "quarter",
                                "year",
                            ],
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(expense_date >= '2022-01-01') AND (expense_date <= '2022-03-31')",
                            "fields": ["amount", "expense_date"],
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="finance_l3_3",
            inputs=Query(
                query="What percentage of total 2023 expenses were Operational vs Capital?",
                output_type=ExpensePercentage,
            ),
            expected_output=QueryResult(
                result=ExpensePercentage(
                    total_expenses=5570,
                    operational_expenses=2220,
                    capital_expenses=1700,
                    operational_percentage=39.86,
                    capital_percentage=30.52,
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(expense_date >= '2023-01-01') AND (expense_date <= '2023-12-31')",
                            "fields": ["amount", "category"],
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="finance_l3_4",
            inputs=Query(
                query="List categories with their total revenue, ordered by highest performing category",
                output_type=CategoryTotals,
            ),
            expected_output=QueryResult(
                result=CategoryTotals(
                    category_totals=[
                        CategoryTotal(category="Software", total_revenue=10850),
                        CategoryTotal(category="Electronics", total_revenue=10500),
                        CategoryTotal(category="Hardware", total_revenue=9150),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_products",
                            "related": "finance_revenues_by_product_id",
                            "fields": ["category", "name"],
                        },
                    ),
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)
