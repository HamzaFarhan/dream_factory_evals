from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]

class StaffInfo(BaseModel):
    employee_name: str
    date_joined: date
    email: str

class DepartmentStaffPolicy(BaseModel):
    department_name: str
    staff: list[StaffInfo]
    policy_title: str
    policy_effective_date: date

class DepartmentStaffPolicies(BaseModel):
    department_staff_policies: list[DepartmentStaffPolicy]

class DepartmentsWithGap(BaseModel):
    departments_with_gap: list[str]

class DepartmentTimingAnalysisItem(BaseModel):
    department_name: str
    policy_date: date
    manager_joined_date: date
    days_difference: int
    timing_pattern: str

class DepartmentTimingAnalysis(BaseModel):
    department_timing_analysis: list[DepartmentTimingAnalysisItem]
    average_days_difference: float
    insight: str

class RoleDistributionAnalysisItem(BaseModel):
    department_name: str
    policy_date: date
    managers: int
    staff: int
    manager_to_staff_ratio: float | None
    balanced_rating: str

class RoleDistributionAnalysis(BaseModel):
    role_distribution_analysis: list[RoleDistributionAnalysisItem]
    insight: str

class PolicyFirstDepartment(BaseModel):
    department_name: str
    policy_effective_date: date
    first_employee_joined: date
    days_delay: int
    employee_name: str
    employee_role: str

class PolicyFirstDepartments(BaseModel):
    policy_first_departments: list[PolicyFirstDepartment]
    average_delay: float
    insight: str
