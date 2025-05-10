from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


class QuarterlyAnalysisItem(BaseModel):
    quarter: str
    software_products: list[str]
    total_revenue: int
    capital_expenses: int
    roi: float | None
    notes: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuarterlyAnalysisItem):
            return NotImplemented
        return (
            self.quarter == other.quarter
            and self.software_products == other.software_products
            and self.total_revenue == other.total_revenue
            and self.capital_expenses == other.capital_expenses
            and self.roi == other.roi
            and are_strings_similar(self.notes, other.notes)
        )


class QuarterlyAnalysis(BaseModel):
    quarterly_analysis: list[QuarterlyAnalysisItem]
    summary: str


class Q1Profit(BaseModel):
    q1_2022_profit: int


class ExpensePercentage(BaseModel):
    total_expenses: int
    operational_expenses: int
    capital_expenses: int
    operational_percentage: float
    capital_percentage: float


class CategoryTotal(BaseModel):
    category: str
    total_revenue: int


class CategoryTotals(BaseModel):
    category_totals: list[CategoryTotal]
