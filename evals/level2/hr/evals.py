from __future__ import annotations

import argparse
from datetime import date as date_
from functools import partial

from output_types import (
    DepartmentCounts,
    DepartmentEmployeeCount,
    DepartmentManager,
    DepartmentPolicyInfo,
    DepartmentsWithPolicy,
    EmployeeDepartment,
    ManagerDepartmentInfo,
    ManagersWithDepartments,
)
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


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = (
    EmployeeDepartment | DepartmentManager | DepartmentCounts | DepartmentsWithPolicy | ManagersWithDepartments
)

hr_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="hr_l2_1",
            inputs=Query(query="What department does Alice Johnson work in?", output_type=EmployeeDepartment),
            expected_output=QueryResult(
                result=EmployeeDepartment(employee="Alice Johnson", department="Sales"),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(first_name='Alice') AND (last_name='Johnson')",
                            "related": "hr_departments_by_department_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="hr_l2_2",
            inputs=Query(query="Who is the manager of the Engineering department?", output_type=DepartmentManager),
            expected_output=QueryResult(
                result=DepartmentManager(
                    first_name="Carol",
                    last_name="Williams",
                    email="carol.williams@example.com",
                    department="Engineering",
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_departments",
                            "filter": "name='Engineering'",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(department_id=3) AND (role='Manager')",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l2_3",
            inputs=Query(query="How many employees are in each department?", output_type=DepartmentCounts),
            expected_output=QueryResult(
                result=DepartmentCounts(
                    department_counts=[
                        DepartmentEmployeeCount(department_name="Sales", employee_count=1),
                        DepartmentEmployeeCount(department_name="Marketing", employee_count=1),
                        DepartmentEmployeeCount(department_name="Engineering", employee_count=1),
                        DepartmentEmployeeCount(department_name="HR", employee_count=1),
                        DepartmentEmployeeCount(department_name="Finance", employee_count=1),
                        DepartmentEmployeeCount(department_name="Operations", employee_count=1),
                        DepartmentEmployeeCount(department_name="Customer Service", employee_count=1),
                        DepartmentEmployeeCount(department_name="IT", employee_count=1),
                        DepartmentEmployeeCount(department_name="Legal", employee_count=1),
                        DepartmentEmployeeCount(department_name="Procurement", employee_count=1),
                        DepartmentEmployeeCount(department_name="R&D", employee_count=1),
                        DepartmentEmployeeCount(department_name="Administration", employee_count=1),
                        DepartmentEmployeeCount(department_name="Support", employee_count=1),
                        DepartmentEmployeeCount(department_name="Quality Assurance", employee_count=1),
                        DepartmentEmployeeCount(department_name="Logistics", employee_count=1),
                        DepartmentEmployeeCount(department_name="Business Development", employee_count=1),
                        DepartmentEmployeeCount(department_name="Strategy", employee_count=1),
                        DepartmentEmployeeCount(department_name="Compliance", employee_count=1),
                        DepartmentEmployeeCount(department_name="Production", employee_count=1),
                        DepartmentEmployeeCount(department_name="Innovation", employee_count=1),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_departments",
                            "related": "hr_employees_by_department_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l2_4",
            inputs=Query(
                query="Which departments have a policy that became effective in 2023?",
                output_type=DepartmentsWithPolicy,
            ),
            expected_output=QueryResult(
                result=DepartmentsWithPolicy(
                    departments=[
                        DepartmentPolicyInfo(
                            department_name="Support",
                            policy_title="Support Policy",
                            effective_date=date(2023, 1, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Quality Assurance",
                            policy_title="Quality Assurance Policy",
                            effective_date=date(2023, 2, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Logistics",
                            policy_title="Logistics Policy",
                            effective_date=date(2023, 3, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Business Development",
                            policy_title="Business Development Policy",
                            effective_date=date(2023, 4, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Strategy",
                            policy_title="Strategy Policy",
                            effective_date=date(2023, 5, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Compliance",
                            policy_title="Compliance Policy",
                            effective_date=date(2023, 6, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Production",
                            policy_title="Production Policy",
                            effective_date=date(2023, 7, 1),
                        ),
                        DepartmentPolicyInfo(
                            department_name="Innovation",
                            policy_title="Innovation Policy",
                            effective_date=date(2023, 8, 1),
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "(effective_date >= '2023-01-01') AND (effective_date <= '2023-12-31')",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="hr_l2_5",
            inputs=Query(
                query="List all managers along with their departments.", output_type=ManagersWithDepartments
            ),
            expected_output=QueryResult(
                result=ManagersWithDepartments(
                    managers=[
                        ManagerDepartmentInfo(
                            first_name="Carol",
                            last_name="Williams",
                            department="Engineering",
                        ),
                        ManagerDepartmentInfo(
                            first_name="Eve",
                            last_name="Davis",
                            department="Finance",
                        ),
                        ManagerDepartmentInfo(
                            first_name="Henry",
                            last_name="Moore",
                            department="IT",
                        ),
                        ManagerDepartmentInfo(
                            first_name="Kelly",
                            last_name="Thomas",
                            department="R&D",
                        ),
                        ManagerDepartmentInfo(
                            first_name="Noah",
                            last_name="Harris",
                            department="Quality Assurance",
                        ),
                        ManagerDepartmentInfo(
                            first_name="Quinn",
                            last_name="Garcia",
                            department="Strategy",
                        ),
                        ManagerDepartmentInfo(
                            first_name="Tyler",
                            last_name="Clark",
                            department="Innovation",
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "role='Manager'",
                            "related": "hr_departments_by_department_id",
                        },
                    ),
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()
    user_role = Role.HR
    name = "hr_level2"
    report = hr_dataset.evaluate_sync(task=partial(task, user_role=user_role, model=args.model), name=name)
    print(report)


if __name__ == "__main__":
    main()
