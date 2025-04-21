from typing import Annotated

from pydantic import BaseModel, Field

# All types are str, even dates (no datetime)

date = Annotated[str, Field(description="format: YYYY-MM-DD")]

class TotalRevenue(BaseModel):
    total_revenue: float

class ProductCount(BaseModel):
    product_count: int

class TotalAmount(BaseModel):
    total_amount: float

class RevenueAmount(BaseModel):
    revenue_amount: float

class Expense(BaseModel):
    expense_id: int
    description: str
    amount: float

class Expenses(BaseModel):
    expenses: list[Expense]
