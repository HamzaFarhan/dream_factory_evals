from __future__ import annotations

from datetime import date as date_

import logfire
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    ToolCall,
)

from .output_types import (
    AnalysisSummary,
    CohortAnalysis,
    CompetencyDevelopmentInitiative,
    Department,
    DepartmentRecruitingAnalysis,
    Employee,
    EngineeringAnalysisResponse,
    HRDepartmentContext,
    HREmployeeProfile,
    Policy,
    PolicyAnalysis,
    PolicyRecruitmentResponse,
    PolicyRecruitmentSuggestion,
    RecruitingEmployee,
    RoleDistribution,
    StrategicCompetencyResponse,
    TalentRecommendation,
)

_ = logfire.configure()


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = EngineeringAnalysisResponse | PolicyRecruitmentResponse | StrategicCompetencyResponse

hr_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="hr_l4_1",
            inputs=Query(
                query="Analyze the profile of employees in the 'Engineering' department who joined in 2023 versus those who joined in 2022 (consider data as of 2024-01-01 for cut-offs). For each group, detail their roles and confirm their department. Also, list any 'Engineering Policy' (from `hr_policies` table, associated with the Engineering department) that became effective between 2022-01-01 and 2024-01-01 (inclusive), including the policy's associated department name. Discuss which of these policies would have been active for a significant portion of each cohort's tenure up to 2024-01-01. What patterns emerge regarding role distribution for these two cohorts? Based on these patterns and policy context, provide two actionable recommendations for HR regarding talent management in the Engineering department.",
                output_type=EngineeringAnalysisResponse,
            ),
            expected_output=QueryResult(
                result=EngineeringAnalysisResponse(
                    analysis_summary=AnalysisSummary(
                        engineering_cohort_2023_joiners=CohortAnalysis(
                            count=3,
                            employees=[
                                Employee(
                                    employee_id=18,
                                    first_name="Anna",
                                    last_name="Baker",
                                    role="Staff",
                                    date_joined="2023-01-24",
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                                Employee(
                                    employee_id=16,
                                    first_name="Diana",
                                    last_name="Foster",
                                    role="Manager",
                                    date_joined="2023-04-08",
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                                Employee(
                                    employee_id=24,
                                    first_name="Tasha",
                                    last_name="Valencia",
                                    role="Staff",
                                    date_joined="2023-11-29",
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                            ],
                            role_distribution=RoleDistribution(Manager=1, Staff=2),
                            relevant_active_policies_by_2024_01_01=[
                                Policy(
                                    policy_id=7,
                                    title="Engineering Policy",
                                    effective_date="2023-06-27",
                                    description="Policy details for Engineering department.",
                                    department_id=3,
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                                Policy(
                                    policy_id=6,
                                    title="Engineering Policy",
                                    effective_date="2023-10-30",
                                    description="Policy details for Engineering department.",
                                    department_id=3,
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                            ],
                        ),
                        engineering_cohort_2022_joiners=CohortAnalysis(
                            count=3,
                            employees=[
                                Employee(
                                    employee_id=23,
                                    first_name="Patrick",
                                    last_name="Ferrell",
                                    role="Staff",
                                    date_joined="2022-07-07",
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                                Employee(
                                    employee_id=21,
                                    first_name="Brandon",
                                    last_name="Rodriguez",
                                    role="Lead",
                                    date_joined="2022-08-06",
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                                Employee(
                                    employee_id=20,
                                    first_name="Whitney",
                                    last_name="Hicks",
                                    role="Staff",
                                    date_joined="2022-12-25",
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                            ],
                            role_distribution=RoleDistribution(Lead=1, Staff=2),
                            relevant_active_policies_by_2024_01_01=[
                                Policy(
                                    policy_id=7,
                                    title="Engineering Policy",
                                    effective_date="2023-06-27",
                                    description="Policy details for Engineering department.",
                                    department_id=3,
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                                Policy(
                                    policy_id=6,
                                    title="Engineering Policy",
                                    effective_date="2023-10-30",
                                    description="Policy details for Engineering department.",
                                    department_id=3,
                                    hr_departments_by_department_id=Department(
                                        department_id=3, name="Engineering", manager_id=16
                                    ),
                                ),
                            ],
                        ),
                        observed_patterns="The 2023 cohort includes a Manager, while the 2022 cohort includes a Lead. Both cohorts are small (3 employees each) and predominantly Staff. Both cohorts experienced the same new Engineering policies (ID 7 and 6) becoming active during their tenure (specifically in 2023).",
                        policy_context_discussion="Policies ID 7 (eff. 2023-06-27) and ID 6 (eff. 2023-10-30) would have been active for the entirety of the 2023 cohort's latter half of their first year, and for the 2022 cohort during their second year of employment. Given the generic descriptions, their specific impact is hard to determine without more content, but their introduction signifies recent updates to Engineering's operational guidelines.",
                    ),
                    recommendations_for_talent_management=[
                        TalentRecommendation(
                            recommendation="Develop targeted onboarding and integration support for new managers joining Engineering, as seen with the 2023 cohort, potentially leveraging insights from the recent policy updates (ID 6 and 7) if they pertain to operational changes.",
                            justification="Based on the pattern of a manager joining in 2023 and new policies becoming active.",
                        ),
                        TalentRecommendation(
                            recommendation="Investigate career progression paths from Staff to Lead within Engineering, as the 2022 cohort shows a Lead. Ensure new policies support skill development for such transitions.",
                            justification="Based on the presence of a Lead in the 2022 cohort and the need to align policies with career growth.",
                        ),
                    ],
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_departments",
                            "filter": "name='Engineering'",
                            "fields": "department_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(department_id=3) AND (date_joined >= '2023-01-01') AND (date_joined <= '2023-12-31')",
                            "fields": [
                                "employee_id",
                                "first_name",
                                "last_name",
                                "role",
                                "date_joined",
                                "department_id",
                            ],
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(department_id=3) AND (date_joined >= '2022-01-01') AND (date_joined <= '2022-12-31')",
                            "fields": [
                                "employee_id",
                                "first_name",
                                "last_name",
                                "role",
                                "date_joined",
                                "department_id",
                            ],
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "(department_id=3) AND (effective_date >= '2022-01-01') AND (effective_date <= '2024-01-01')",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l4_2",
            inputs=Query(
                query="The general 'HR Policy' (Policy ID 8, effective 2023-05-13) and the specific 'IT Policy' (Policy ID 17, effective 2023-09-21) were introduced. Retrieve these policies along with their associated department names. Analyze their `description` (assume HR Policy applies company-wide). Then, by examining the `role` and `department_name` for employees in the 'IT' and 'Sales' departments who joined between 2023-06-02 and 2024-01-01 (inclusive), what potential impact could these policies have on attracting talent to these departments? Provide two distinct suggestions for leveraging aspects of these policies in recruitment materials for roles in these departments, considering their generic descriptions.",
                output_type=PolicyRecruitmentResponse,
            ),
            expected_output=QueryResult(
                result=PolicyRecruitmentResponse(
                    policy_analysis_summary=[
                        PolicyAnalysis(
                            policy_id=8,
                            title="HR Policy",
                            effective_date="2023-05-13",
                            description="Policy details for HR department.",
                            department_id=4,
                            department_name="HR",
                            applicable_scope="Company-wide",
                        ),
                        PolicyAnalysis(
                            policy_id=17,
                            title="IT Policy",
                            effective_date="2023-09-21",
                            description="Policy details for IT department.",
                            department_id=9,
                            department_name="IT",
                            applicable_scope="IT Department specific",
                        ),
                    ],
                    recruitment_period_analysis={
                        "IT": DepartmentRecruitingAnalysis(
                            count=2,
                            roles=["Staff", "Lead"],
                            employees=[
                                RecruitingEmployee(
                                    employee_id=19,
                                    first_name="Zachary",
                                    last_name="Taylor",
                                    role="Staff",
                                    date_joined="2023-08-30",
                                    department_name="IT",
                                ),
                                RecruitingEmployee(
                                    employee_id=15,
                                    first_name="Samuel",
                                    last_name="Wilson",
                                    role="Lead",
                                    date_joined="2023-10-17",
                                    department_name="IT",
                                ),
                            ],
                        ),
                        "Sales": DepartmentRecruitingAnalysis(
                            count=1,
                            roles=["Staff"],
                            employees=[
                                RecruitingEmployee(
                                    employee_id=25,
                                    first_name="Victor",
                                    last_name="Brown",
                                    role="Staff",
                                    date_joined="2023-12-08",
                                    department_name="Sales",
                                ),
                            ],
                        ),
                    },
                    policy_impact_assessment="The IT Policy (effective Sept 2023) coincides with the recruitment of a Lead role in October 2023, suggesting possible alignment between specialized policies and higher-level roles. The general HR Policy (May 2023) preceded all recent hires in both departments, potentially establishing foundation for recruitment across the organization.",
                    recruitment_suggestions=[
                        PolicyRecruitmentSuggestion(
                            department="IT",
                            suggestion="Emphasize the newly established IT Policy as evidence of the company's commitment to structured and modern IT operations.",
                            justification="The policy's recent implementation (September 2023) demonstrates organizational focus on the IT department, potentially attractive to candidates seeking well-defined work environments.",
                            target_roles=["Staff", "Lead"],
                        ),
                        PolicyRecruitmentSuggestion(
                            department="Sales",
                            suggestion="Highlight the company-wide HR Policy as foundation for employee development across all departments, including Sales.",
                            justification="With only general HR Policy applicable to Sales (no Sales-specific policy evident), focus on how the foundational HR guidelines support employee success regardless of department.",
                            target_roles=["Staff", "Manager"],
                        ),
                    ],
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records_by_ids",
                        params={
                            "table_name": "hr_policies",
                            "ids": [8, 17],
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={"table_name": "hr_departments", "filter": "name IN ('IT', 'Sales')"},
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(department_id IN (9, 7)) AND (date_joined >= '2023-06-02') AND (date_joined <= '2024-01-01')",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l4_3",
            inputs=Query(
                query="The 'HR' department (department_id 4) is strategically emphasizing data-driven decision-making, a direction supported by the existing 'HR Policy' (Policy ID 8, effective 2023-05-13). Considering this strategic push, and imagining the department aims to cultivate more specialized data and systems skills within its existing 'Staff' and 'Lead' roles (particularly for those who joined after 2023-01-01), identify three key future-facing competencies the HR department should develop. For each competency, propose one specific development initiative.",
                output_type=StrategicCompetencyResponse,
            ),
            expected_output=QueryResult(
                result=StrategicCompetencyResponse(
                    strategic_context=HRDepartmentContext(
                        department_id=4,
                        department_name="HR",
                        policy_details=Policy(
                            policy_id=8,
                            title="HR Policy",
                            effective_date="2023-05-13",
                            description="Policy details for HR department.",
                            department_id=4,
                            hr_departments_by_department_id=Department(department_id=4, name="HR", manager_id=11),
                        ),
                        strategic_direction="Data-driven decision-making",
                        targeted_roles=["Staff", "Lead"],
                    ),
                    current_hr_team_profile=HREmployeeProfile(
                        count=2,
                        roles={"Staff": 1, "Lead": 1},
                        join_dates=["2023-02-12", "2023-09-08"],
                    ),
                    proposed_competency_initiatives=[
                        CompetencyDevelopmentInitiative(
                            competency="HR Analytics",
                            initiative_name="HR Metrics & KPI Mastery Program",
                            description="Training series focused on identifying, measuring, and interpreting key HR performance indicators to generate actionable insights for leadership.",
                            target_roles=["Staff", "Lead"],
                            expected_outcome="Ability to design and implement data collection frameworks, generate meaningful reports, and provide data-backed recommendations for talent management decisions.",
                        ),
                        CompetencyDevelopmentInitiative(
                            competency="HRIS Technical Expertise",
                            initiative_name="HR Systems Implementation & Management Certification",
                            description="Structured learning path covering HR information systems architecture, configuration, integration capabilities, and advanced reporting features.",
                            target_roles=["Lead", "Staff"],
                            expected_outcome="Capability to serve as system administrators for HR tools, optimize workflows through automation, and extract maximum value from HR technology investments.",
                        ),
                        CompetencyDevelopmentInitiative(
                            competency="Predictive Workforce Planning",
                            initiative_name="Future Workforce Modeling Workshop Series",
                            description="Interactive workshops combining statistical modeling techniques with HR domain knowledge to develop predictive capabilities for talent needs.",
                            target_roles=["Lead"],
                            expected_outcome="Skills to forecast hiring needs, identify emerging skill gaps, predict turnover patterns, and develop proactive talent strategies aligned with business objectives.",
                        ),
                    ],
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={"table_name": "hr_departments", "filter": "department_id=4"},
                    ),
                    ToolCall(
                        tool_name="get_table_records_by_ids",
                        params={
                            "table_name": "hr_policies",
                            "ids": [8],
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(department_id=4) AND (role IN ('Staff', 'Lead')) AND (date_joined >= '2023-01-01')",
                        },
                    ),
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)
