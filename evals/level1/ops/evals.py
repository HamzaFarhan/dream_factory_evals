from __future__ import annotations

import argparse
from functools import partial

import logfire
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

from .output_types import (
    ActiveMachines,
    Machine,
    Machines,
    MachineStatus,
    ReplacementCount,
)

_ = logfire.configure()

ResultT = ActiveMachines | MachineStatus | Machines | ReplacementCount

ops_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="ops_l1_q1",
            inputs=Query(query="How many machines are currently active?", output_type=ActiveMachines),
            expected_output=QueryResult(
                result=ActiveMachines(active_machines=12),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "status='Active'",
                            "fields": "machine_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l1_q2",
            inputs=Query(query="What is the current status of Machine 5?", output_type=MachineStatus),
            expected_output=QueryResult(
                result=MachineStatus(machine_name="Machine 5", status="Active"),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "machine_name='Machine 5'",
                            "fields": ["machine_name", "status"],
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l1_q3",
            inputs=Query(query="List all machines installed in 2022.", output_type=Machines),
            expected_output=QueryResult(
                result=Machines(
                    machines=[
                        Machine(machine_id=13, machine_name="Machine 13", location="Fort Worth"),
                        Machine(machine_id=14, machine_name="Machine 14", location="Columbus"),
                        Machine(machine_id=15, machine_name="Machine 15", location="Charlotte"),
                        Machine(machine_id=16, machine_name="Machine 16", location="San Francisco"),
                        Machine(machine_id=17, machine_name="Machine 17", location="Indianapolis"),
                        Machine(machine_id=18, machine_name="Machine 18", location="Seattle"),
                        Machine(machine_id=19, machine_name="Machine 19", location="Denver"),
                        Machine(machine_id=20, machine_name="Machine 20", location="Washington"),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "(installation_date >= '2022-01-01') AND (installation_date <= '2022-12-31')",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l1_q4",
            inputs=Query(
                query="How many maintenance actions involved part replacements in 2023?",
                output_type=ReplacementCount,
            ),
            expected_output=QueryResult(
                result=ReplacementCount(replacement_count=2),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_maintenance",
                            "filter": "(maintenance_action='Replaced part') AND (maintenance_date >= '2023-01-01') AND (maintenance_date <= '2023-12-31')",
                            "fields": "maintenance_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l1_q5",
            inputs=Query(query="Which machines are currently under maintenance?", output_type=Machines),
            expected_output=QueryResult(
                result=Machines(
                    machines=[
                        Machine(machine_id=2, machine_name="Machine 2", location="Los Angeles"),
                        Machine(machine_id=6, machine_name="Machine 6", location="Philadelphia"),
                        Machine(machine_id=11, machine_name="Machine 11", location="Austin"),
                        Machine(machine_id=16, machine_name="Machine 16", location="San Francisco"),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "status='Maintenance'",
                        },
                    )
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)


def main():
    parser = argparse.ArgumentParser(description="Run OPS evaluations")
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

    model = args.model
    user_role = Role.OPS
    name = f"{model.upper()}-{user_role.value.upper()}-LEVEL-1"

    report = ops_dataset.evaluate_sync(task=partial(task, user_role=user_role, model=model), name=name)
    print(f"Evaluation report for {args.model}:")
    print(report)


if __name__ == "__main__":
    main()
