from datetime import date

from pydantic import BaseModel


class Email(BaseModel):
    email: str


class DepartmentCount(BaseModel):
    department_count: int


class Policy(BaseModel):
    policy_id: int
    title: str
    description: str
    effective_date: date
    department_id: int


class Policies(BaseModel):
    policies: list[Policy]


class Employee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    email: str
    date_joined: date
    department_id: int
    role: str


class Employees(BaseModel):
    employees: list[Employee]


class ManagerCount(BaseModel):
    manager_count: int


class TotalRevenue(BaseModel):
    total_revenue: int


class ProductCount(BaseModel):
    product_count: int


class TotalAmount(BaseModel):
    total_amount: int


class RevenueAmount(BaseModel):
    revenue_amount: int


class Expense(BaseModel):
    expense_id: int
    description: str
    amount: int


class Expenses(BaseModel):
    expenses: list[Expense]


class ActiveMachines(BaseModel):
    active_machines: int


class MachineStatus(BaseModel):
    machine_name: str
    status: str


class Machine(BaseModel):
    machine_id: int
    machine_name: str
    location: str


class Machines(BaseModel):
    machines: list[Machine]


class ReplacementCount(BaseModel):
    replacement_count: int
