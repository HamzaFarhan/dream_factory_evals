from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DepartmentTimingAnalysisItem):
            return NotImplemented
        return (
            self.department_name == other.department_name
            and self.policy_date == other.policy_date
            and self.manager_joined_date == other.manager_joined_date
            and self.days_difference == other.days_difference
            and are_strings_similar(self.timing_pattern, other.timing_pattern)
        )


class DepartmentTimingAnalysis(BaseModel):
    department_timing_analysis: list[DepartmentTimingAnalysisItem]
    average_days_difference: float
    insight: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DepartmentTimingAnalysis):
            return NotImplemented
        return (
            self.department_timing_analysis == other.department_timing_analysis
            and self.average_days_difference == other.average_days_difference
            and are_strings_similar(self.insight, other.insight)
        )


class RoleDistributionAnalysisItem(BaseModel):
    department_name: str
    policy_date: date
    managers: int
    staff: int
    manager_to_staff_ratio: float | None
    balanced_rating: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoleDistributionAnalysisItem):
            return NotImplemented
        return (
            self.department_name == other.department_name
            and self.policy_date == other.policy_date
            and self.managers == other.managers
            and self.staff == other.staff
            and self.manager_to_staff_ratio == other.manager_to_staff_ratio
            and are_strings_similar(self.balanced_rating, other.balanced_rating)
        )


class RoleDistributionAnalysis(BaseModel):
    role_distribution_analysis: list[RoleDistributionAnalysisItem]
    insight: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoleDistributionAnalysis):
            return NotImplemented
        return self.role_distribution_analysis == other.role_distribution_analysis and are_strings_similar(
            self.insight, other.insight
        )


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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PolicyFirstDepartments):
            return NotImplemented
        return (
            self.policy_first_departments == other.policy_first_departments
            and self.average_delay == other.average_delay
            and are_strings_similar(self.insight, other.insight)
        )
