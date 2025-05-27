from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


# Common models
class Department(BaseModel):
    department_id: int
    name: str
    manager_id: int


class Policy(BaseModel):
    policy_id: int
    title: str
    effective_date: date
    description: str
    department_id: int
    hr_departments_by_department_id: Department | None = None


class Employee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    role: str
    date_joined: date
    hr_departments_by_department_id: Department | None = None


# Query 1 models
class RoleDistribution(BaseModel):
    Manager: int | None = None
    Lead: int | None = None
    Staff: int | None = None


class CohortAnalysis(BaseModel):
    count: int
    employees: list[Employee]
    role_distribution: RoleDistribution
    relevant_active_policies_by_2024_01_01: list[Policy]


class AnalysisSummary(BaseModel):
    engineering_cohort_2023_joiners: CohortAnalysis
    engineering_cohort_2022_joiners: CohortAnalysis
    observed_patterns: str
    policy_context_discussion: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AnalysisSummary):
            return NotImplemented
        return (
            self.engineering_cohort_2023_joiners == other.engineering_cohort_2023_joiners
            and self.engineering_cohort_2022_joiners == other.engineering_cohort_2022_joiners
            and are_strings_similar(self.observed_patterns, other.observed_patterns)
            and are_strings_similar(self.policy_context_discussion, other.policy_context_discussion)
        )


class TalentRecommendation(BaseModel):
    recommendation: str
    justification: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TalentRecommendation):
            return NotImplemented
        return are_strings_similar(self.recommendation, other.recommendation) and are_strings_similar(
            self.justification, other.justification
        )


class EngineeringAnalysisResponse(BaseModel):
    analysis_summary: AnalysisSummary
    recommendations_for_talent_management: list[TalentRecommendation]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EngineeringAnalysisResponse):
            return NotImplemented
        return (
            self.analysis_summary == other.analysis_summary
            and self.recommendations_for_talent_management == other.recommendations_for_talent_management
        )


# Query 2 models
class PolicyAnalysis(BaseModel):
    policy_id: int
    title: str
    effective_date: date
    description: str
    department_id: int | None = None
    department_name: str | None = None
    applicable_scope: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PolicyAnalysis):
            return NotImplemented
        return (
            self.policy_id == other.policy_id
            and are_strings_similar(self.title, other.title)
            and self.effective_date == other.effective_date
            and are_strings_similar(self.description, other.description)
            and self.department_id == other.department_id
            and (
                self.department_name == other.department_name
                if self.department_name is None or other.department_name is None
                else are_strings_similar(self.department_name, other.department_name)
            )
            and are_strings_similar(self.applicable_scope, other.applicable_scope)
        )


class RecruitingEmployee(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    role: str
    date_joined: date
    department_name: str


class DepartmentRecruitingAnalysis(BaseModel):
    count: int
    roles: list[str]
    employees: list[RecruitingEmployee]


class PolicyRecruitmentSuggestion(BaseModel):
    department: str
    suggestion: str
    justification: str
    target_roles: list[str]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PolicyRecruitmentSuggestion):
            return NotImplemented
        return (
            are_strings_similar(self.department, other.department)
            and are_strings_similar(self.suggestion, other.suggestion)
            and are_strings_similar(self.justification, other.justification)
            and self.target_roles == other.target_roles
        )


class PolicyRecruitmentResponse(BaseModel):
    policy_analysis_summary: list[PolicyAnalysis]
    recruitment_period_analysis: dict[str, DepartmentRecruitingAnalysis]
    policy_impact_assessment: str
    recruitment_suggestions: list[PolicyRecruitmentSuggestion]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PolicyRecruitmentResponse):
            return NotImplemented
        return (
            self.policy_analysis_summary == other.policy_analysis_summary
            and self.recruitment_period_analysis == other.recruitment_period_analysis
            and are_strings_similar(self.policy_impact_assessment, other.policy_impact_assessment)
            and self.recruitment_suggestions == other.recruitment_suggestions
        )


# Query 3 models
class HRDepartmentContext(BaseModel):
    department_id: int
    department_name: str
    policy_details: Policy
    strategic_direction: str
    targeted_roles: list[str]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HRDepartmentContext):
            return NotImplemented
        return (
            self.department_id == other.department_id
            and are_strings_similar(self.department_name, other.department_name)
            and self.policy_details == other.policy_details
            and are_strings_similar(self.strategic_direction, other.strategic_direction)
            and self.targeted_roles == other.targeted_roles
        )


class HREmployeeProfile(BaseModel):
    count: int
    roles: dict[str, int]
    join_dates: list[date]


class CompetencyDevelopmentInitiative(BaseModel):
    competency: str
    initiative_name: str
    description: str
    target_roles: list[str]
    expected_outcome: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CompetencyDevelopmentInitiative):
            return NotImplemented
        return (
            are_strings_similar(self.competency, other.competency)
            and are_strings_similar(self.initiative_name, other.initiative_name)
            and are_strings_similar(self.description, other.description)
            and self.target_roles == other.target_roles
            and are_strings_similar(self.expected_outcome, other.expected_outcome)
        )


class StrategicCompetencyResponse(BaseModel):
    strategic_context: HRDepartmentContext
    current_hr_team_profile: HREmployeeProfile
    proposed_competency_initiatives: list[CompetencyDevelopmentInitiative]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StrategicCompetencyResponse):
            return NotImplemented
        return (
            self.strategic_context == other.strategic_context
            and self.current_hr_team_profile == other.current_hr_team_profile
            and self.proposed_competency_initiatives == other.proposed_competency_initiatives
        )
