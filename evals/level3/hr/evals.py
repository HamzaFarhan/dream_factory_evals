from __future__ import annotations

import argparse
from datetime import date as date_
from functools import partial

from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    Role,
    ToolCall,
    task,
)

from .types import (
    DepartmentStaffPolicies,
    DepartmentStaffPolicy,
    DepartmentsWithGap,
    DepartmentTimingAnalysis,
    DepartmentTimingAnalysisItem,
    PolicyFirstDepartment,
    PolicyFirstDepartments,
    RoleDistributionAnalysis,
    RoleDistributionAnalysisItem,
    StaffInfo,
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


HR_RESULT_TYPES = (
    DepartmentStaffPolicies
    | DepartmentsWithGap
    | DepartmentTimingAnalysis
    | RoleDistributionAnalysis
    | PolicyFirstDepartments
)

hr_dataset = Dataset[Query, QueryResult](
    cases=[
        Case(
            name="hr_l3_1",
            inputs=Query(
                query="Find all staff members who joined in 2023 and group them by department, along with their respective department policies.",
                result_type=DepartmentStaffPolicies,
            ),
            expected_output=QueryResult(
                result=DepartmentStaffPolicies(
                    department_staff_policies=[
                        DepartmentStaffPolicy(
                            department_name="Support",
                            staff=[
                                StaffInfo(
                                    employee_name="Mia White",
                                    date_joined="2023-01-15",
                                    email="mia.white@example.com",
                                )
                            ],
                            policy_title="Support Policy",
                            policy_effective_date="2023-01-01",
                        ),
                        DepartmentStaffPolicy(
                            department_name="Logistics",
                            staff=[
                                StaffInfo(
                                    employee_name="Olivia Martin",
                                    date_joined="2023-03-05",
                                    email="olivia.martin@example.com",
                                )
                            ],
                            policy_title="Logistics Policy",
                            policy_effective_date="2023-03-01",
                        ),
                        DepartmentStaffPolicy(
                            department_name="Business Development",
                            staff=[
                                StaffInfo(
                                    employee_name="Peter Thompson",
                                    date_joined="2023-04-20",
                                    email="peter.thompson@example.com",
                                )
                            ],
                            policy_title="Business Development Policy",
                            policy_effective_date="2023-04-01",
                        ),
                        DepartmentStaffPolicy(
                            department_name="Compliance",
                            staff=[
                                StaffInfo(
                                    employee_name="Riley Martinez",
                                    date_joined="2023-06-10",
                                    email="riley.martinez@example.com",
                                )
                            ],
                            policy_title="Compliance Policy",
                            policy_effective_date="2023-06-01",
                        ),
                        DepartmentStaffPolicy(
                            department_name="Production",
                            staff=[
                                StaffInfo(
                                    employee_name="Sophia Robinson",
                                    date_joined="2023-07-05",
                                    email="sophia.robinson@example.com",
                                )
                            ],
                            policy_title="Production Policy",
                            policy_effective_date="2023-07-01",
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(role='Staff') AND (date_joined >= '2023-01-01') AND (date_joined <= '2023-12-31')",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "department_id IN (13, 15, 16, 18, 19)",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l3_2",
            inputs=Query(
                query="Identify departments that have policies effective in the first half of 2023 but don't have any employees who joined in the same period.",
                result_type=DepartmentsWithGap,
            ),
            expected_output=QueryResult(
                result=DepartmentsWithGap(departments_with_gap=[]),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "(effective_date >= '2023-01-01') AND (effective_date <= '2023-06-30')",
                        },
                    ),
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(date_joined > '2023-06-30') AND (department_id IN (13, 14, 15, 16, 17, 18))",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l3_3",
            inputs=Query(
                query="Calculate the average time between policy implementation and manager appointments for each department in 2022-2023.",
                result_type=DepartmentTimingAnalysis,
            ),
            expected_output=QueryResult(
                result=DepartmentTimingAnalysis(
                    department_timing_analysis=[
                        DepartmentTimingAnalysisItem(
                            department_name="Engineering",
                            policy_date="2022-03-01",
                            manager_joined_date="2022-03-05",
                            days_difference=4,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                        DepartmentTimingAnalysisItem(
                            department_name="Finance",
                            policy_date="2022-05-01",
                            manager_joined_date="2022-05-15",
                            days_difference=14,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                        DepartmentTimingAnalysisItem(
                            department_name="IT",
                            policy_date="2022-08-01",
                            manager_joined_date="2022-08-20",
                            days_difference=19,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                        DepartmentTimingAnalysisItem(
                            department_name="R&D",
                            policy_date="2022-11-01",
                            manager_joined_date="2022-11-05",
                            days_difference=4,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                        DepartmentTimingAnalysisItem(
                            department_name="Quality Assurance",
                            policy_date="2023-02-01",
                            manager_joined_date="2023-02-10",
                            days_difference=9,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                        DepartmentTimingAnalysisItem(
                            department_name="Strategy",
                            policy_date="2023-05-01",
                            manager_joined_date="2023-05-15",
                            days_difference=14,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                        DepartmentTimingAnalysisItem(
                            department_name="Innovation",
                            policy_date="2023-08-01",
                            manager_joined_date="2023-08-20",
                            days_difference=19,
                            timing_pattern="Manager joined after policy implementation",
                        ),
                    ],
                    average_days_difference=11.86,
                    insight="Managers typically join departments shortly after policy implementation, with an average delay of about 12 days.",
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "fields": ["employee_id", "date_joined", "department_id"],
                            "filter": "(role='Manager') AND (date_joined >= '2022-01-01') AND (date_joined <= '2023-12-31')",
                        },
                    ),
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "department_id IN (3, 5, 8, 11, 14, 17, 20) AND (effective_date >= '2022-01-01') AND (effective_date <= '2023-12-31')",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l3_4",
            inputs=Query(
                query="Analyze the distribution of employees by role across departments that have policies implemented in 2023 and identify which departments have the most balanced ratio of managers to staff.",
                result_type=RoleDistributionAnalysis,
            ),
            expected_output=QueryResult(
                result=RoleDistributionAnalysis(
                    role_distribution_analysis=[
                        RoleDistributionAnalysisItem(
                            department_name="Support",
                            policy_date="2023-01-01",
                            managers=0,
                            staff=1,
                            manager_to_staff_ratio=0,
                            balanced_rating="No managers",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Quality Assurance",
                            policy_date="2023-02-01",
                            managers=1,
                            staff=0,
                            manager_to_staff_ratio=None,
                            balanced_rating="No staff",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Logistics",
                            policy_date="2023-03-01",
                            managers=0,
                            staff=1,
                            manager_to_staff_ratio=0,
                            balanced_rating="No managers",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Business Development",
                            policy_date="2023-04-01",
                            managers=0,
                            staff=1,
                            manager_to_staff_ratio=0,
                            balanced_rating="No managers",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Strategy",
                            policy_date="2023-05-01",
                            managers=1,
                            staff=0,
                            manager_to_staff_ratio=None,
                            balanced_rating="No staff",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Compliance",
                            policy_date="2023-06-01",
                            managers=0,
                            staff=1,
                            manager_to_staff_ratio=0,
                            balanced_rating="No managers",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Production",
                            policy_date="2023-07-01",
                            managers=0,
                            staff=1,
                            manager_to_staff_ratio=0,
                            balanced_rating="No managers",
                        ),
                        RoleDistributionAnalysisItem(
                            department_name="Innovation",
                            policy_date="2023-08-01",
                            managers=1,
                            staff=0,
                            manager_to_staff_ratio=None,
                            balanced_rating="No staff",
                        ),
                    ],
                    insight="None of the departments with 2023 policies have both managers and staff. Three departments (Quality Assurance, Strategy, Innovation) have only managers, while five departments have only staff members. This suggests potential management or staffing imbalances across departments with newly implemented policies.",
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "(effective_date >= '2023-01-01') AND (effective_date <= '2023-12-31')",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "department_id IN (13, 14, 15, 16, 17, 18, 19, 20)",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l3_5",
            inputs=Query(
                query="Identify departments where the policy was implemented before any employees joined, and calculate the average delay between policy implementation and the first employee joining these departments.",
                result_type=PolicyFirstDepartments,
            ),
            expected_output=QueryResult(
                result=PolicyFirstDepartments(
                    policy_first_departments=[
                        PolicyFirstDepartment(
                            department_name="Sales",
                            policy_effective_date="2022-01-01",
                            first_employee_joined="2022-01-15",
                            days_delay=14,
                            employee_name="Alice Johnson",
                            employee_role="Staff",
                        ),
                        PolicyFirstDepartment(
                            department_name="Marketing",
                            policy_effective_date="2022-02-01",
                            first_employee_joined="2022-02-10",
                            days_delay=9,
                            employee_name="Bob Smith",
                            employee_role="Staff",
                        ),
                        PolicyFirstDepartment(
                            department_name="Engineering",
                            policy_effective_date="2022-03-01",
                            first_employee_joined="2022-03-05",
                            days_delay=4,
                            employee_name="Carol Williams",
                            employee_role="Manager",
                        ),
                        PolicyFirstDepartment(
                            department_name="HR",
                            policy_effective_date="2022-04-01",
                            first_employee_joined="2022-04-20",
                            days_delay=19,
                            employee_name="David Brown",
                            employee_role="Staff",
                        ),
                        PolicyFirstDepartment(
                            department_name="Finance",
                            policy_effective_date="2022-05-01",
                            first_employee_joined="2022-05-15",
                            days_delay=14,
                            employee_name="Eve Davis",
                            employee_role="Manager",
                        ),
                        PolicyFirstDepartment(
                            department_name="Operations",
                            policy_effective_date="2022-06-01",
                            first_employee_joined="2022-06-10",
                            days_delay=9,
                            employee_name="Frank Miller",
                            employee_role="Staff",
                        ),
                        PolicyFirstDepartment(
                            department_name="Customer Service",
                            policy_effective_date="2022-07-01",
                            first_employee_joined="2022-07-05",
                            days_delay=4,
                            employee_name="Grace Wilson",
                            employee_role="Staff",
                        ),
                        PolicyFirstDepartment(
                            department_name="IT",
                            policy_effective_date="2022-08-01",
                            first_employee_joined="2022-08-20",
                            days_delay=19,
                            employee_name="Henry Moore",
                            employee_role="Manager",
                        ),
                    ],
                    average_delay=11.5,
                    insight="All departments established in 2022 had their policies implemented before any employees joined, with an average delay of 11.5 days between policy implementation and the first employee joining. Departments that first hired managers tended to have more varied delays (4-19 days) compared to those that first hired staff.",
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "fields": ["policy_id", "title", "effective_date", "department_id"],
                            "order_by": "effective_date ASC",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "fields": [
                                "employee_id",
                                "first_name",
                                "last_name",
                                "date_joined",
                                "department_id",
                                "role",
                            ],
                            "order_by": "date_joined ASC",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult(), EvaluateToolCalls()],
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()
    user_role = Role.HR
    name = f"level3_hr_{args.model}"
    report = hr_dataset.evaluate_sync(task=partial(task, user_role=user_role, model=args.model), name=name)
    print(report)


if __name__ == "__main__":
    main()
