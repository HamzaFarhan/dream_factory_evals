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
    MachineAgeInfo,
    MachineAnomalyInfo,
    MachineLocation,
    MachineMaintenanceInfo,
    MachinesWithAnomalies,
    MaintenanceActionCount,
    MaintenanceStatusInfo,
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


OPS_RESULT_TYPES = (
    MachineMaintenanceInfo
    | MaintenanceStatusInfo
    | MaintenanceActionCount
    | MachinesWithAnomalies
    | MachineAgeInfo
)

ops_dataset = Dataset[Query, QueryResult](
    cases=[
        Case(
            name="ops_l2_1",
            inputs=Query(
                query="When was the last maintenance performed on Machine 5 and what action was taken?",
                output_type=MachineMaintenanceInfo,
            ),
            expected_output=QueryResult(
                result=MachineMaintenanceInfo(
                    machine_name="Machine 5",
                    machine_status="Active",
                    last_maintenance_date="2022-05-05",
                    maintenance_action="Replaced part",
                    notes="Minor malfunction fixed.",
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_maintenance",
                            "filter": "machine_id=5",
                            "order_field": "maintenance_date DESC",
                            "limit": 1,
                            "related": "ops_machines_by_machine_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l2_2",
            inputs=Query(
                query="How many machines are currently in 'Maintenance' status, and where are they located?",
                output_type=MaintenanceStatusInfo,
            ),
            expected_output=QueryResult(
                result=MaintenanceStatusInfo(
                    maintenance_count=4,
                    machines=[
                        MachineLocation(machine_name="Machine 2", location="Los Angeles"),
                        MachineLocation(machine_name="Machine 6", location="Philadelphia"),
                        MachineLocation(machine_name="Machine 11", location="Austin"),
                        MachineLocation(machine_name="Machine 16", location="San Francisco"),
                    ],
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "status='Maintenance'",
                            "fields": ["machine_name", "location"],
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l2_3",
            inputs=Query(
                query="Compare the number of maintenance actions categorized as 'Routine check' versus 'Replaced part' in 2022.",
                output_type=MaintenanceActionCount,
            ),
            expected_output=QueryResult(
                result=MaintenanceActionCount(
                    routine_check_count=6,
                    replaced_part_count=3,
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_maintenance",
                            "filter": "(maintenance_date >= '2022-01-01') AND (maintenance_date <= '2022-12-31')",
                            "fields": ["maintenance_action"],
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l2_4",
            inputs=Query(
                query="List all machines with anomalies detected during maintenance in 2023, along with the maintenance notes.",
                output_type=MachinesWithAnomalies,
            ),
            expected_output=QueryResult(
                result=MachinesWithAnomalies(
                    machines_with_anomalies=[
                        MachineAnomalyInfo(
                            machine_name="Machine 15",
                            maintenance_date="2023-03-25",
                            notes="Component replaced due to wear.",
                        ),
                        MachineAnomalyInfo(
                            machine_name="Machine 20",
                            maintenance_date="2023-08-20",
                            notes="Replaced due to malfunction.",
                        ),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_maintenance",
                            "filter": "(maintenance_date >= '2023-01-01') AND (maintenance_date <= '2023-12-31') AND (anomaly_detected=true)",
                            "fields": ["maintenance_date", "notes", "machine_id"],
                            "related": "ops_machines_by_machine_id",
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l2_5",
            inputs=Query(
                query="What is the average age (in years) of machines in 'Active' status as of December 31, 2023?",
                output_type=MachineAgeInfo,
            ),
            expected_output=QueryResult(
                result=MachineAgeInfo(
                    average_age_years=2.15,
                    active_machine_count=12,
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "(status='Active') AND (installation_date <= '2023-12-31')",
                            "fields": ["installation_date"],
                        },
                    )
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
    user_role = Role.OPS
    name = f"level2_ops_{args.model}"
    report = ops_dataset.evaluate_sync(task=partial(task, user_role=user_role, model=args.model), name=name)
    print(report)


if __name__ == "__main__":
    main()
