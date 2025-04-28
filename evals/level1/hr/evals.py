from __future__ import annotations

import argparse
from datetime import date as date_

import logfire
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    Role,
    ToolCall,
    evaluate,
)

from .output_types import (
    DepartmentCount,
    Email,
    Employee,
    Employees,
    Expense,
    Expenses,
    Machine,
    Machines,
    MachineStatus,
    ManagerCount,
    Policies,
    Policy,
    ProductCount,
    ReplacementCount,
    RevenueAmount,
    TotalAmount,
    TotalRevenue,
)

_ = logfire.configure()


HR_RESULT_TYPES = (
    Email
    | DepartmentCount
    | Employee
    | Employees
    | Expense
    | Expenses
    | Machine
    | Machines
    | MachineStatus
    | ManagerCount
    | Policies
    | Policy
    | ProductCount
    | ReplacementCount
    | RevenueAmount
    | TotalAmount
    | TotalRevenue
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


# @dataclass
# class EvaluateResult(Evaluator[Query, QueryResult]):
#     def evaluate(self, ctx: EvaluatorContext[Query, QueryResult]) -> bool:
#         if ctx.expected_output is None:
#             return True
#         return ctx.output.result == ctx.expected_output.result


# @dataclass
# class EvaluateToolCalls(Evaluator[Query, QueryResult]):
#     def evaluate(self, ctx: EvaluatorContext[Query, QueryResult]) -> EvaluationReason:
#         if ctx.expected_output is None:
#             return EvaluationReason(value=True)
#         if len(ctx.output.tool_calls) > len(ctx.expected_output.tool_calls):
#             return EvaluationReason(
#                 value=False,
#                 reason=f"Too many tool calls: {len(ctx.output.tool_calls)} > {len(ctx.expected_output.tool_calls)}",
#             )
#         reason = ""
#         tool_num = 1
#         for output_tool_call, expected_tool_call in zip(ctx.output.tool_calls, ctx.expected_output.tool_calls):
#             if output_tool_call.tool != expected_tool_call.tool:
#                 reason += f"Tool call mismatch: {output_tool_call.tool} != {expected_tool_call.tool} at tool number: {tool_num}\n"
#             if sorted(output_tool_call.params) != sorted(expected_tool_call.params):
#                 reason += f"Tool call params mismatch: {output_tool_call.params} != {expected_tool_call.params} at tool number: {tool_num}\n"
#             tool_num += 1
#         if reason:
#             return EvaluationReason(value=False, reason=reason)
#         return EvaluationReason(value=True)


hr_dataset = Dataset[Query, QueryResult](
    cases=[
        Case(
            name="hr_l1_q1",
            inputs=Query(query="What is the email address of Alice Johnson?", output_type=Email),
            expected_output=QueryResult(
                result=Email(email="alice.johnson@example.com"),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(first_name='Alice') AND (last_name='Johnson')",
                            "fields": "email",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="hr_l1_q2",
            inputs=Query(query="How many departments do we have in the company?", output_type=DepartmentCount),
            expected_output=QueryResult(
                result=DepartmentCount(department_count=20),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_departments",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="hr_l1_q3",
            inputs=Query(
                query="List all department policies that were effective from January to June 2023.",
                output_type=Policies,
            ),
            expected_output=QueryResult(
                result=Policies(
                    policies=[
                        Policy(
                            policy_id=13,
                            title="Support Policy",
                            description="Policy details for Support department.",
                            effective_date=date(2023, 1, 1),
                            department_id=13,
                        ),
                        Policy(
                            policy_id=14,
                            title="Quality Assurance Policy",
                            description="Policy details for Quality Assurance department.",
                            effective_date=date(2023, 2, 1),
                            department_id=14,
                        ),
                        Policy(
                            policy_id=15,
                            title="Logistics Policy",
                            description="Policy details for Logistics department.",
                            effective_date=date(2023, 3, 1),
                            department_id=15,
                        ),
                        Policy(
                            policy_id=16,
                            title="Business Development Policy",
                            description="Policy details for Business Development department.",
                            effective_date=date(2023, 4, 1),
                            department_id=16,
                        ),
                        Policy(
                            policy_id=17,
                            title="Strategy Policy",
                            description="Policy details for Strategy department.",
                            effective_date=date(2023, 5, 1),
                            department_id=17,
                        ),
                        Policy(
                            policy_id=18,
                            title="Compliance Policy",
                            description="Policy details for Compliance department.",
                            effective_date=date(2023, 6, 1),
                            department_id=18,
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_policies",
                            "filter": "(effective_date >= '2023-01-01') AND (effective_date <= '2023-06-30')",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="hr_l1_q4",
            inputs=Query(query="List all employees who joined in 2023.", output_type=Employees),
            expected_output=QueryResult(
                result=Employees(
                    employees=[
                        Employee(
                            employee_id=13,
                            first_name="Mia",
                            last_name="White",
                            email="mia.white@example.com",
                            date_joined=date(2023, 1, 15),
                            department_id=13,
                            role="Staff",
                        ),
                        Employee(
                            employee_id=14,
                            first_name="Noah",
                            last_name="Harris",
                            email="noah.harris@example.com",
                            date_joined=date(2023, 2, 10),
                            department_id=14,
                            role="Manager",
                        ),
                        Employee(
                            employee_id=15,
                            first_name="Olivia",
                            last_name="Martin",
                            email="olivia.martin@example.com",
                            date_joined=date(2023, 3, 5),
                            department_id=15,
                            role="Staff",
                        ),
                        Employee(
                            employee_id=16,
                            first_name="Peter",
                            last_name="Thompson",
                            email="peter.thompson@example.com",
                            date_joined=date(2023, 4, 20),
                            department_id=16,
                            role="Staff",
                        ),
                        Employee(
                            employee_id=17,
                            first_name="Quinn",
                            last_name="Garcia",
                            email="quinn.garcia@example.com",
                            date_joined=date(2023, 5, 15),
                            department_id=17,
                            role="Manager",
                        ),
                        Employee(
                            employee_id=18,
                            first_name="Riley",
                            last_name="Martinez",
                            email="riley.martinez@example.com",
                            date_joined=date(2023, 6, 10),
                            department_id=18,
                            role="Staff",
                        ),
                        Employee(
                            employee_id=19,
                            first_name="Sophia",
                            last_name="Robinson",
                            email="sophia.robinson@example.com",
                            date_joined=date(2023, 7, 5),
                            department_id=19,
                            role="Staff",
                        ),
                        Employee(
                            employee_id=20,
                            first_name="Tyler",
                            last_name="Clark",
                            email="tyler.clark@example.com",
                            date_joined=date(2023, 8, 20),
                            department_id=20,
                            role="Manager",
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "(date_joined >= '2023-01-01') AND (date_joined <= '2023-12-31')",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="hr_l1_q5",
            inputs=Query(query="How many managers do we have in the company?", output_type=ManagerCount),
            expected_output=QueryResult(
                result=ManagerCount(manager_count=7),
                tool_calls=[
                    ToolCall(
                        tool="get_table_records",
                        params={
                            "table_name": "hr_employees",
                            "filter": "role='Manager'",
                            "fields": "employee_id",
                        },
                    )
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult(), EvaluateToolCalls()],
)


def main():
    parser = argparse.ArgumentParser(description="Run HR evaluations")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name to evaluate. Examples:\n"
        "  OpenAI: 'openai:gpt-4-turbo', 'openai:gpt-4o'\n"
        "  Anthropic: 'anthropic:claude-3-5-sonnet-latest', 'anthropic:claude-3-opus-latest'\n"
        "  Google: 'google-gla:gemini-1.5-pro', 'google-gla:gemini-1.5-flash'",
    )
    args = parser.parse_args()

    evaluate(model=args.model, dataset=hr_dataset, user_role=Role.HR, level=1)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    for model in models:
        evaluate(model=model, dataset=hr_dataset, user_role=Role.HR, level=1)
