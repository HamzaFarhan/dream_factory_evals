from __future__ import annotations

from datetime import date as date_

import logfire
from output_types import (
    AgeStatusCount,
    AnalysisAndIntervention,
    AnomalyEventsAnalysisResponse,
    AnomalyEventsByMachine,
    AverageAgeByStatus,
    LocationComparison,
    LocationMachineAnalysis,
    LocationMaintenanceAnalysisResponse,
    MachineAgeAnalysisResponse,
    MachineMaintenanceEvent,
    MaintenanceActionBreakdown,
    MaintenanceRecord,
    MostFrequentAnomalyMachine,
    OldestMachineMaintenance,
    StrategicSuggestion,
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
    ToolCall,
    evaluate,
)

_ = logfire.configure()


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


ResultT = LocationMaintenanceAnalysisResponse | AnomalyEventsAnalysisResponse | MachineAgeAnalysisResponse

ops_dataset = Dataset[Query[ResultT], QueryResult[ResultT]](
    cases=[
        Case(
            name="ops_l4_1",
            inputs=Query(
                query="Identify machines installed before 2023-01-01 located in 'East Jessetown'. For these machines, count the total number of maintenance events recorded in the year 2024 (Jan 1st to Dec 31st). Categorize these 2024 maintenance events by `maintenance_action`. Compare this maintenance profile (total count and action breakdown) to machines installed before 2023-01-01 located in 'Robinsonshire'. Based on the comparison, suggest one specific area where maintenance strategy might need adjustment for one of the locations.",
                output_type=LocationMaintenanceAnalysisResponse,
            ),
            expected_output=QueryResult(
                result=LocationMaintenanceAnalysisResponse(
                    analysis_period="2024-01-01 to 2024-12-31",
                    machine_installation_cutoff="Before 2023-01-01",
                    location_comparison=LocationComparison(
                        East_Jessetown=LocationMachineAnalysis(
                            machines_analyzed_ids=[1, 18, 21, 22, 71, 72, 73, 92],
                            total_2024_maintenance_events=6,
                            maintenance_action_breakdown_2024=MaintenanceActionBreakdown(
                                Routine_check=2,
                                Calibration=2,
                                Software_update=1,
                                Replaced_part=1,
                            ),
                        ),
                        Robinsonshire=LocationMachineAnalysis(
                            machines_analyzed_ids=[12, 13, 15, 16, 17, 50, 51, 52, 53],
                            total_2024_maintenance_events=10,
                            maintenance_action_breakdown_2024=MaintenanceActionBreakdown(
                                Routine_check=1,
                                Calibration=3,
                                Software_update=1,
                                Replaced_part=5,
                            ),
                        ),
                    ),
                    strategic_suggestion=StrategicSuggestion(
                        observation="Older machines (installed before 2023) in Robinsonshire had significantly more maintenance events in 2024 (10 vs 6) compared to East Jessetown, with a notably higher number of 'Replaced part' actions (5 vs 1).",
                        suggestion="Investigate the root cause for the higher rate of part replacements in older machines at the Robinsonshire location. This could indicate more severe wear and tear, environmental factors, or potentially less effective preventative maintenance compared to East Jessetown. Consider adjusting the preventative maintenance schedule or component inspection frequency specifically for older assets in Robinsonshire.",
                    ),
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "installation_date < '2023-01-01' AND location = 'East Jessetown'",
                            "fields": ["machine_id", "location", "installation_date"],
                            "related": "ops_maintenance_by_machine_id",
                        },
                    ),
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "installation_date < '2023-01-01' AND location = 'Robinsonshire'",
                            "fields": ["machine_id", "location", "installation_date"],
                            "related": "ops_maintenance_by_machine_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="ops_l4_2",
            inputs=Query(
                query="Identify all maintenance events in 2023 and 2024 where `anomaly_detected` was true. For each such event, list the machine name, location, status (from `ops_machines`), maintenance date, maintenance action, and notes. Group these anomaly events by machine. Which machine had the most anomalies detected across these two years? For that specific machine, analyze the sequence of maintenance actions and notes associated with its anomalies. Is there a recurring issue suggested by the data? Recommend a next step for addressing the issues with this machine.",
                output_type=AnomalyEventsAnalysisResponse,
            ),
            expected_output=QueryResult(
                result=AnomalyEventsAnalysisResponse(
                    analysis_period="2023-01-01 to 2024-12-31",
                    anomaly_events_by_machine=AnomalyEventsByMachine(
                        anomaly_events_by_machine={
                            "Machine 54": [
                                MachineMaintenanceEvent(
                                    maintenance_date="2023-11-23",
                                    maintenance_action="Software update",
                                    notes="System reboot failed.",
                                    anomaly_detected=True,
                                    location="Lake Roberto",
                                    status="Maintenance",
                                ),
                                MachineMaintenanceEvent(
                                    maintenance_date="2024-01-22",
                                    maintenance_action="Routine check",
                                    notes="Anomaly found during routine check.",
                                    anomaly_detected=True,
                                    location="Lake Roberto",
                                    status="Maintenance",
                                ),
                                MachineMaintenanceEvent(
                                    maintenance_date="2024-02-21",
                                    maintenance_action="Calibration",
                                    notes="Calibration unsuccessful.",
                                    anomaly_detected=True,
                                    location="Lake Roberto",
                                    status="Maintenance",
                                ),
                                MachineMaintenanceEvent(
                                    maintenance_date="2024-03-22",
                                    maintenance_action="Replaced part",
                                    notes="Part incompatible.",
                                    anomaly_detected=True,
                                    location="Lake Roberto",
                                    status="Maintenance",
                                ),
                            ]
                        }
                    ),
                    most_frequent_anomaly_machine=MostFrequentAnomalyMachine(
                        machine_id=54,
                        machine_name="Machine 54",
                        location="Lake Roberto",
                        status="Maintenance",
                        anomaly_count=4,
                        analysis="Machine 54 has had continuous issues from November 2023 through March 2024, with each maintenance attempt resulting in a new anomaly. The progression from software issues to calibration problems to hardware incompatibility suggests a systemic problem that isn't being properly diagnosed and addressed.",
                        recommendation="Conduct a comprehensive diagnostic assessment of Machine 54, possibly bringing in a specialist. Rather than continuing the pattern of incremental fixes, consider a full system reset or component replacement as the recurring issues across software, calibration, and hardware point to potential interdependent failures.",
                    ),
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_maintenance",
                            "filter": "(maintenance_date >= '2023-01-01' AND maintenance_date <= '2024-12-31') AND anomaly_detected = true",
                            "fields": [
                                "machine_id",
                                "maintenance_date",
                                "maintenance_action",
                                "notes",
                                "anomaly_detected",
                            ],
                            "related": "ops_machines_by_machine_id",
                        },
                    ),
                ],
            ),
        ),
        Case(
            name="ops_l4_3",
            inputs=Query(
                query="Calculate the average age (as of 2025-01-01) of machines currently in 'Active' status versus those in 'Maintenance' status. For machines currently in 'Maintenance' status, retrieve their last 3 maintenance records (if available), including the machine name, location, maintenance date, action, and notes. Analyze the recent maintenance history (last 3 events) for the two oldest machines currently in 'Maintenance' status. Are there common themes in their recent maintenance actions or notes that might explain their current status? Suggest a potential intervention for one of these older machines.",
                output_type=MachineAgeAnalysisResponse,
            ),
            expected_output=QueryResult(
                result=MachineAgeAnalysisResponse(
                    analysis_date="2025-01-01",
                    average_machine_age_by_status=AverageAgeByStatus(
                        Active=AgeStatusCount(count=76, average_age_years=3.2),
                        Maintenance=AgeStatusCount(count=24, average_age_years=3.7),
                    ),
                    recent_maintenance_for_oldest_maintenance_machines=[
                        OldestMachineMaintenance(
                            machine_id=9,
                            machine_name="Machine 9",
                            location="North Jameschester",
                            status="Maintenance",
                            installation_date="2020-03-18",
                            age_years=4.8,
                            last_3_maintenance=[
                                MaintenanceRecord(
                                    maintenance_date="2024-11-15",
                                    maintenance_action="Replaced part",
                                    notes="Component failure due to age.",
                                ),
                                MaintenanceRecord(
                                    maintenance_date="2024-09-12",
                                    maintenance_action="Routine check",
                                    notes="Performance degradation noted.",
                                ),
                                MaintenanceRecord(
                                    maintenance_date="2024-06-03",
                                    maintenance_action="Calibration",
                                    notes="Calibration within acceptable range.",
                                ),
                            ],
                        ),
                        OldestMachineMaintenance(
                            machine_id=28,
                            machine_name="Machine 28",
                            location="Lake Roberto",
                            status="Maintenance",
                            installation_date="2020-07-21",
                            age_years=4.5,
                            last_3_maintenance=[
                                MaintenanceRecord(
                                    maintenance_date="2024-12-18",
                                    maintenance_action="Software update",
                                    notes="Update failed, retrying.",
                                ),
                                MaintenanceRecord(
                                    maintenance_date="2024-10-22",
                                    maintenance_action="Replaced part",
                                    notes="Temporary fix until full replacement available.",
                                ),
                                MaintenanceRecord(
                                    maintenance_date="2024-07-15",
                                    maintenance_action="Calibration",
                                    notes="Calibration unsuccessful, scheduled for re-attempt.",
                                ),
                            ],
                        ),
                    ],
                    analysis_and_intervention_suggestion=AnalysisAndIntervention(
                        analysis="The two oldest machines in maintenance status (Machine 9 at 4.8 years and Machine 28 at 4.5 years) show different failure patterns. Machine 9's issues appear age-related with component failures and performance degradation, but maintenance actions have been appropriate. Machine 28, however, shows a pattern of unsuccessful maintenance attempts across software, hardware, and calibration, indicating more systemic issues. Both machines are significantly older than the average for maintenance status machines (3.7 years).",
                        intervention_suggestion="For Machine 28, given the pattern of unsuccessful maintenance across multiple systems (software updates failing, temporary part replacements, and unsuccessful calibration), a comprehensive overhaul rather than incremental fixes is recommended. Schedule it for complete refurbishment instead of continued point solutions, as the series of failures indicates end-of-life service issues that won't be resolved with the current approach of isolated repairs.",
                    ),
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="get_table_records",
                        params={
                            "table_name": "ops_machines",
                            "filter": "status = 'Active' OR status = 'Maintenance'",
                            "fields": ["machine_id", "machine_name", "location", "status", "installation_date"],
                            "related": "ops_maintenance_by_machine_id",
                        },
                    )
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
                name=f"{model}-{Role.OPS.value}-level-4", model=model, user_role=Role.OPS, level=4
            ),
            dataset=ops_dataset,
        )
