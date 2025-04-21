from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]

class ProductRevenueInfo(BaseModel):
    product_name: str
    revenue_amount: int
    category: str

class CategoryRevenueComparison(BaseModel):
    electronics_revenue: int
    software_revenue: int

class ProfitInfo(BaseModel):
    total_revenue: int
    total_expenses: int
    profit: int

class HardwareRevenue(BaseModel):
    product_name: str
    revenue_amount: int

class HardwareRevenues(BaseModel):
    hardware_revenues: list[HardwareRevenue]

class ExpenseComparison(BaseModel):
    capital_expenses: int
    operational_expenses: int
