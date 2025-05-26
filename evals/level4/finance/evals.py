from __future__ import annotations

from datetime import date as date_

import logfire
from output_types import (
    AnalysisAndStrategySuggestion,
    CapitalExpense,
    CategoryQuarterlyRevenue,
    CategoryRevenue,
    CategoryYoYRevenue,
    CorrelationAnalysisAndRecommendation,
    FinanceL4Query1Response,
    FinanceL4Query2Response,
    FinanceL4Query3Response,
    OperationalExpensesYoY,
    QualitativeAssessmentAndRoiSuggestion,
    QuarterlyAmount,
    RevenueAnalysis,
    RevenueComparisonYoY,
)
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    ReportInfo,
    Role,
    ToolCall,
    evaluate,
)

_ = logfire.configure()


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = FinanceL4Query1Response | FinanceL4Query2Response | FinanceL4Query3Response

finance_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="finance_l4_1",
            inputs=Query(
                query="For the full year 2024, identify the top 2 product categories by total revenue. For each of these top categories, detail their quarterly revenue. Separately, calculate the total 'Operational' expenses for each quarter of 2024. Analyze if there's any apparent correlation between the quarterly operational expense trends and the quarterly revenue trends of the top product categories. Provide one strategic recommendation for optimizing operational efficiency or revenue generation based on this analysis.",
                output_type=FinanceL4Query1Response,
            ),
            expected_output=QueryResult(
                result=FinanceL4Query1Response(
                    year_analyzed=2024,
                    top_product_categories_by_revenue=[
                        CategoryQuarterlyRevenue(
                            category_name="Electronics",
                            total_revenue_2024=112799.13,
                            quarterly_revenue=QuarterlyAmount(
                                Q1=8786.37,
                                Q2=52748.88,
                                Q3=16694.27,
                                Q4=34569.61,
                                total=112799.13,
                            ),
                        ),
                        CategoryQuarterlyRevenue(
                            category_name="Service",
                            total_revenue_2024=82099.01,
                            quarterly_revenue=QuarterlyAmount(
                                Q1=17900.71,
                                Q2=9025.19,
                                Q3=24863.67,
                                Q4=30309.44,
                                total=82099.01,
                            ),
                        ),
                    ],
                    quarterly_operational_expenses_2024=QuarterlyAmount(
                        Q1=8438.42,
                        Q2=304.96,
                        Q3=0.0,
                        Q4=974.98,
                        total=9718.36,
                    ),
                    correlation_analysis_and_recommendation=CorrelationAnalysisAndRecommendation(
                        analysis_summary="Electronics revenue peaked in Q2 (52748.88) and Q4 (34569.61). Service revenue was strong in Q3 (24863.67) and Q4 (30309.44). Operational expenses were highest in Q1 (8438.42) and much lower in subsequent quarters, particularly Q3 (0.00). There isn't a clear direct correlation between quarterly operational expense spikes and revenue peaks in the top categories for 2024; revenues seem driven by other factors. The significant drop in Q3 operational expenses while Service revenue was strong and Electronics revenue was moderate is notable.",
                        strategic_recommendation="Investigate the cause of the near-zero operational expenses in Q3 2024. If this represents a sustainable efficiency gain without negatively impacting Q3/Q4 revenue generation (especially for Services), try to replicate these efficiencies in other quarters. Otherwise, ensure Q3 was not an anomaly that could risk future operations if critical spending was merely deferred.",
                    ),
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(year=2024)",
                            "fields": ["revenue_amount", "quarter", "product_id"],
                            "related": "finance_products_by_product_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(category='Operational') AND (expense_date >= '2024-01-01') AND (expense_date <= '2024-12-31')",
                            "fields": ["amount", "expense_date"],
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="finance_l4_2",
            inputs=Query(
                query="Identify all 'Capital' expenses recorded in the year 2023, listing their description, amount, and expense date. Concurrently, for products in the 'Electronics' and 'Hardware' categories, calculate their total revenue for Q4 2023 and for each quarter of 2024. Based on the descriptions of the 2023 capital expenses and the revenue performance of 'Electronics' and 'Hardware' products in 2024, is there any qualitative indication that these investments might have started to impact revenues? Provide a brief assessment and suggest one area for further quantitative ROI analysis.",
                output_type=FinanceL4Query2Response,
            ),
            expected_output=QueryResult(
                result=FinanceL4Query2Response(
                    capital_expenses_2023=[
                        CapitalExpense(
                            expense_id=17,
                            description="Technology infrastructure",
                            amount=1722.63,
                            expense_date="2023-07-24",
                        ),
                        CapitalExpense(
                            expense_id=13,
                            description="Land purchase",
                            amount=1813.33,
                            expense_date="2023-08-16",
                        ),
                        CapitalExpense(
                            expense_id=15,
                            description="Land purchase",
                            amount=1708.48,
                            expense_date="2023-12-07",
                        ),
                    ],
                    revenue_analysis=RevenueAnalysis(
                        Electronics=CategoryRevenue(
                            Q4_2023_revenue=13831.28,
                            quarterly_revenue_for_2024=QuarterlyAmount(
                                Q1=8786.37,
                                Q2=52748.88,
                                Q3=16694.27,
                                Q4=34569.61,
                                total=112799.13,
                            ),
                        ),
                        Hardware=CategoryRevenue(
                            Q4_2023_revenue=0.0,
                            quarterly_revenue_for_2024=QuarterlyAmount(
                                Q1=0.0,
                                Q2=8842.21,
                                Q3=0.0,
                                Q4=3012.43,
                                total=11854.64,
                            ),
                        ),
                    ),
                    qualitative_assessment_and_roi_suggestion=QualitativeAssessmentAndRoiSuggestion(
                        assessment="The 'Technology infrastructure' capital expense in July 2023 (1722.63) could potentially be linked to the strong performance of 'Electronics' products in 2024, especially the significant Q2 2024 revenue. 'Hardware' products show revenue in 2024 where there was none in Q4 2023, which might also be influenced by general infrastructure improvements or other unlisted capital expenditures. 'Land purchases' are less likely to have an immediate direct impact on product revenue in these categories within this timeframe.",
                        roi_suggestion="A more detailed quantitative ROI analysis should be performed on the 'Technology infrastructure' investment (Expense ID 17) by correlating its deployment specifics (if available) with the product lifecycle and sales data of high-performing 'Electronics' products in 2024.",
                    ),
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(category='Capital') AND (expense_date >= '2023-01-01') AND (expense_date <= '2023-12-31')",
                            "fields": ["expense_id", "description", "amount", "expense_date"],
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "((year=2023) AND (quarter=4)) OR (year=2024)",
                            "fields": ["revenue_amount", "quarter", "year", "product_id"],
                            "related": "finance_products_by_product_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="finance_l4_3",
            inputs=Query(
                query="Compare the total revenue for 'Software' products versus 'Service' products for the full year 2023 and the full year 2024. Calculate the year-over-year revenue growth rate for each of these two categories. Simultaneously, calculate the total 'Operational' expenses for 2023 and 2024, and its year-over-year change. Are the growth trajectories of these two product categories aligned with the overall operational expense trend? If one category shows significantly different growth or potential margin implications relative to operational cost changes, highlight this and suggest one financial strategy to either capitalize on strength or improve performance.",
                output_type=FinanceL4Query3Response,
            ),
            expected_output=QueryResult(
                result=FinanceL4Query3Response(
                    revenue_comparison_yoy=RevenueComparisonYoY(
                        Software=CategoryYoYRevenue(
                            total_revenue_for_2023=38172.46,
                            total_revenue_for_2024=74777.46,
                            yoy_growth_rate_percentage=95.9,
                        ),
                        Service=CategoryYoYRevenue(
                            total_revenue_for_2023=53776.69,
                            total_revenue_for_2024=82099.01,
                            yoy_growth_rate_percentage=52.67,
                        ),
                    ),
                    operational_expenses_yoy=OperationalExpensesYoY(
                        total_operational_expenses_for_2023=10397.51,
                        total_operational_expenses_for_2024=9718.36,
                        yoy_change_percentage=-6.53,
                    ),
                    analysis_and_strategy_suggestion=AnalysisAndStrategySuggestion(
                        analysis="Software products demonstrated exceptionally high YoY revenue growth (95.90%), significantly outpacing Service products (52.67%). Both categories grew while total operational expenses decreased by 6.53%. This suggests improving operational leverage, especially for the Software category. The high growth in Software with decreasing operational costs indicates potentially strong and improving margins for Software products.",
                        financial_strategy="Given Software's strong growth and the favorable operational expense trend, consider re-investing a portion of the efficiency gains (from reduced OpEx) into further accelerating Software product development or marketing to capitalize on its high-growth trajectory and strong margin potential. For Services, while growth is solid, investigate if specific operational efficiencies can be targeted to boost its margin contribution further, or if its growth can be accelerated through targeted investments.",
                    ),
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_revenues",
                            "filter": "(year=2023) OR (year=2024)",
                            "fields": ["revenue_amount", "year", "product_id"],
                            "related": "finance_products_by_product_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "finance_expenses",
                            "filter": "(category='Operational') AND ((expense_date >= '2023-01-01' AND expense_date <= '2023-12-31') OR (expense_date >= '2024-01-01' AND expense_date <= '2024-12-31'))",
                            "fields": ["amount", "expense_date"],
                        },
                    ),
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    for model in models:
        evaluate(
            report_info=ReportInfo(
                name=f"{model}-{Role.FINANCE.value}-level-4", model=model, user_role=Role.FINANCE, level=4
            ),
            dataset=finance_dataset,
        )
