from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


# Common models
class QuarterlyAmount(BaseModel):
    Q1: float
    Q2: float
    Q3: float
    Q4: float
    total: float | None = None


# Finance L4 Query 1 - Top categories and operational expenses
class CategoryQuarterlyRevenue(BaseModel):
    category_name: str
    total_revenue_2024: float
    quarterly_revenue: QuarterlyAmount


class CorrelationAnalysisAndRecommendation(BaseModel):
    analysis_summary: str
    strategic_recommendation: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CorrelationAnalysisAndRecommendation):
            return NotImplemented
        return are_strings_similar(self.analysis_summary, other.analysis_summary) and are_strings_similar(
            self.strategic_recommendation, other.strategic_recommendation
        )


class FinanceL4Query1Response(BaseModel):
    year_analyzed: int
    top_product_categories_by_revenue: list[CategoryQuarterlyRevenue]
    quarterly_operational_expenses_2024: QuarterlyAmount
    correlation_analysis_and_recommendation: CorrelationAnalysisAndRecommendation


# Finance L4 Query 2 - Capital expenses and revenue analysis
class CapitalExpense(BaseModel):
    expense_id: int
    description: str
    amount: float
    expense_date: date


class CategoryRevenue(BaseModel):
    Q4_2023_revenue: float
    quarterly_revenue_for_2024: QuarterlyAmount


class QualitativeAssessmentAndRoiSuggestion(BaseModel):
    assessment: str
    roi_suggestion: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QualitativeAssessmentAndRoiSuggestion):
            return NotImplemented
        return are_strings_similar(self.assessment, other.assessment) and are_strings_similar(
            self.roi_suggestion, other.roi_suggestion
        )


class RevenueAnalysis(BaseModel):
    Electronics: CategoryRevenue
    Hardware: CategoryRevenue


class FinanceL4Query2Response(BaseModel):
    capital_expenses_2023: list[CapitalExpense]
    revenue_analysis: RevenueAnalysis
    qualitative_assessment_and_roi_suggestion: QualitativeAssessmentAndRoiSuggestion


# Finance L4 Query 3 - YoY comparison and strategy
class CategoryYoYRevenue(BaseModel):
    total_revenue_for_2023: float
    total_revenue_for_2024: float
    yoy_growth_rate_percentage: float


class OperationalExpensesYoY(BaseModel):
    total_operational_expenses_for_2023: float
    total_operational_expenses_for_2024: float
    yoy_change_percentage: float


class AnalysisAndStrategySuggestion(BaseModel):
    analysis: str
    financial_strategy: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AnalysisAndStrategySuggestion):
            return NotImplemented
        return are_strings_similar(self.analysis, other.analysis) and are_strings_similar(
            self.financial_strategy, other.financial_strategy
        )


class RevenueComparisonYoY(BaseModel):
    Software: CategoryYoYRevenue
    Service: CategoryYoYRevenue


class FinanceL4Query3Response(BaseModel):
    revenue_comparison_yoy: RevenueComparisonYoY
    operational_expenses_yoy: OperationalExpensesYoY
    analysis_and_strategy_suggestion: AnalysisAndStrategySuggestion
