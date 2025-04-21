from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]

class QuarterlyAnalysisItem(BaseModel):
    quarter: str
    software_products: list[str]
    total_revenue: int
    capital_expenses: int
    roi: float | None
    notes: str

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
