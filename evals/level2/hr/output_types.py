from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


class EmployeeDepartment(BaseModel):
    employee: str
    department: str


class DepartmentManager(BaseModel):
    first_name: str
    last_name: str
    email: str
    department: str


class DepartmentEmployeeCount(BaseModel):
    department_name: str
    employee_count: int


class DepartmentCounts(BaseModel):
    department_counts: list[DepartmentEmployeeCount]


class DepartmentPolicyInfo(BaseModel):
    department_name: str
    policy_title: str
    effective_date: date


class DepartmentsWithPolicy(BaseModel):
    departments: list[DepartmentPolicyInfo]


class ManagerDepartmentInfo(BaseModel):
    first_name: str
    last_name: str
    department: str


class ManagersWithDepartments(BaseModel):
    managers: list[ManagerDepartmentInfo]
