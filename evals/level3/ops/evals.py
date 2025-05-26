from __future__ import annotations

from datetime import date as date_

from output_types import (
    AnomalyRate,
    AnomalyRates,
    InstallationYearComparison,
    InstallationYearComparisonItem,
    MaintenanceByLocation,
)
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    ReportInfo,
    Role,
    TaskConfig,
    ToolCall,
    evaluate,
)


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = MaintenanceByLocation | AnomalyRates | InstallationYearComparison

ops_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="ops_l3_1",
            inputs=Query(
                query="Count the number of maintenance actions for machines in different locations, only for machines installed before 2022.",
                output_type=MaintenanceByLocation,
            ),
            expected_output=QueryResult(
                result=MaintenanceByLocation(
                    maintenance_by_location={
                        "New York": 1,
                        "Los Angeles": 1,
                        "Chicago": 1,
                        "Houston": 1,
                        "Phoenix": 1,
                        "Philadelphia": 1,
                        "San Antonio": 1,
                        "San Diego": 1,
                        "Dallas": 1,
                        "San Jose": 1,
                        "Austin": 1,
                        "Jacksonville": 1,
                    }
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "installation_date < '2022-01-01'",
                            "related": "ops_maintenance_by_machine_id",
                            "fields": ["location", "installation_date"],
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l3_2",
            inputs=Query(
                query="What percentage of maintenance actions resulted in anomaly detection, broken down by machine location?",
                output_type=AnomalyRates,
            ),
            expected_output=QueryResult(
                result=AnomalyRates(
                    anomaly_rates=[
                        AnomalyRate(location="Los Angeles", anomaly_rate=100.0),
                        AnomalyRate(location="Phoenix", anomaly_rate=100.0),
                        AnomalyRate(location="Dallas", anomaly_rate=100.0),
                        AnomalyRate(location="Charlotte", anomaly_rate=100.0),
                        AnomalyRate(location="Washington", anomaly_rate=100.0),
                        AnomalyRate(location="New York", anomaly_rate=0.0),
                        AnomalyRate(location="Chicago", anomaly_rate=0.0),
                        AnomalyRate(location="Houston", anomaly_rate=0.0),
                        AnomalyRate(location="Philadelphia", anomaly_rate=0.0),
                        AnomalyRate(location="San Antonio", anomaly_rate=0.0),
                        AnomalyRate(location="San Diego", anomaly_rate=0.0),
                        AnomalyRate(location="San Jose", anomaly_rate=0.0),
                        AnomalyRate(location="Austin", anomaly_rate=0.0),
                        AnomalyRate(location="Jacksonville", anomaly_rate=0.0),
                        AnomalyRate(location="Fort Worth", anomaly_rate=0.0),
                        AnomalyRate(location="Columbus", anomaly_rate=0.0),
                        AnomalyRate(location="San Francisco", anomaly_rate=0.0),
                        AnomalyRate(location="Indianapolis", anomaly_rate=0.0),
                        AnomalyRate(location="Seattle", anomaly_rate=0.0),
                        AnomalyRate(location="Denver", anomaly_rate=0.0),
                    ]
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "related": "ops_maintenance_by_machine_id",
                            "fields": ["location", "anomaly_detected"],
                        },
                    )
                ],
            ),
        ),
        Case(
            name="ops_l3_3",
            inputs=Query(
                query="Calculate the average time between machine installation and first maintenance for machines installed in 2021 versus 2022.",
                output_type=InstallationYearComparison,
            ),
            expected_output=QueryResult(
                result=InstallationYearComparison(
                    installation_year_comparison={
                        "2021": InstallationYearComparisonItem(
                            total_machines=12,
                            machines_with_maintenance=12,
                            avg_days_to_first_maintenance=365.6,
                        ),
                        "2022": InstallationYearComparisonItem(
                            total_machines=8,
                            machines_with_maintenance=8,
                            avg_days_to_first_maintenance=367.13,
                        ),
                    },
                    insight="Machines installed in 2022 received their first maintenance sooner after installation (367.13 days on average) compared to machines installed in 2021 (365.6 days on average).",
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "installation_date >= '2021-01-01' AND installation_date <= '2021-12-31'",
                            "fields": ["machine_id", "installation_date"],
                            "related": "ops_maintenance_by_machine_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "installation_date >= '2022-01-01' AND installation_date <= '2022-12-31'",
                            "fields": ["machine_id", "installation_date"],
                            "related": "ops_maintenance_by_machine_id",
                        },
                    ),
                ],
            ),
        ),
    ],
    evaluators=[EvaluateResult[ResultT](), EvaluateToolCalls[ResultT]()],
)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    for model in models:
        evaluate(
            report_info=ReportInfo(
                name=f"{model}-{Role.OPS.value}-level-3", model=model, user_role=Role.OPS, level=3
            ),
            dataset=ops_dataset,
            task_config=TaskConfig(user_role=Role.OPS, model=model),
        )
