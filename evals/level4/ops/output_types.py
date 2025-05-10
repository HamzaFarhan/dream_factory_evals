from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


# Common Models
class MachineBase(BaseModel):
    machine_id: int


class MaintenanceEvent(BaseModel):
    maintenance_date: date
    maintenance_action: str
    notes: str
    anomaly_detected: bool | None = None


# Query 1 Models - Location Maintenance Comparison
class MaintenanceActionBreakdown(BaseModel):
    """Breakdown of maintenance actions by type for a specific location."""
    Routine_check: int | None = None
    Calibration: int | None = None
    Software_update: int | None = None
    Replaced_part: int | None = None


class LocationMachineAnalysis(BaseModel):
    """Analysis of machines at a specific location."""
    machines_analyzed_ids: list[int]
    total_2024_maintenance_events: int
    maintenance_action_breakdown_2024: MaintenanceActionBreakdown


class LocationComparison(BaseModel):
    """Comparison of maintenance events between two locations."""
    East_Jessetown: LocationMachineAnalysis
    Robinsonshire: LocationMachineAnalysis


class StrategicSuggestion(BaseModel):
    """Strategic suggestion based on location comparison."""
    observation: str
    suggestion: str


class LocationMaintenanceAnalysisResponse(BaseModel):
    """Response for query ops_l4_1."""
    analysis_period: str
    machine_installation_cutoff: str
    location_comparison: LocationComparison
    strategic_suggestion: StrategicSuggestion

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LocationMaintenanceAnalysisResponse):
            return NotImplemented
        return (
            self.analysis_period == other.analysis_period 
            and self.machine_installation_cutoff == other.machine_installation_cutoff
            and self.location_comparison == other.location_comparison
            and are_strings_similar(self.strategic_suggestion.observation, other.strategic_suggestion.observation)
            and are_strings_similar(self.strategic_suggestion.suggestion, other.strategic_suggestion.suggestion)
        )


# Query 2 Models - Anomaly Events Analysis
class MachineMaintenanceEvent(BaseModel):
    """Maintenance event with machine details."""
    maintenance_date: date
    maintenance_action: str
    notes: str
    anomaly_detected: bool
    location: str
    status: str


class MachineMaintenanceEvents(BaseModel):
    """List of maintenance events for a specific machine."""
    maintenance_events: list[MachineMaintenanceEvent]


class MostFrequentAnomalyMachine(BaseModel):
    """Details of the machine with the most anomalies."""
    machine_id: int
    machine_name: str
    location: str
    status: str
    anomaly_count: int
    analysis: str
    recommendation: str


class AnomalyEventsByMachine(BaseModel):
    """Mapping of machine names to their maintenance events."""
    anomaly_events_by_machine: dict[str, list[MachineMaintenanceEvent]]


class AnomalyEventsAnalysisResponse(BaseModel):
    """Response for query ops_l4_2."""
    analysis_period: str
    anomaly_events_by_machine: AnomalyEventsByMachine
    most_frequent_anomaly_machine: MostFrequentAnomalyMachine

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AnomalyEventsAnalysisResponse):
            return NotImplemented
        return (
            self.analysis_period == other.analysis_period
            and self.anomaly_events_by_machine == other.anomaly_events_by_machine
            and self.most_frequent_anomaly_machine.machine_id == other.most_frequent_anomaly_machine.machine_id
            and self.most_frequent_anomaly_machine.anomaly_count == other.most_frequent_anomaly_machine.anomaly_count
            and are_strings_similar(self.most_frequent_anomaly_machine.analysis, other.most_frequent_anomaly_machine.analysis)
            and are_strings_similar(self.most_frequent_anomaly_machine.recommendation, other.most_frequent_anomaly_machine.recommendation)
        )


# Query 3 Models - Machine Age and Maintenance Analysis
class AgeStatusCount(BaseModel):
    """Count and average age of machines by status."""
    count: int
    average_age_years: float


class AverageAgeByStatus(BaseModel):
    """Average age comparison of machines by their status."""
    Active: AgeStatusCount
    Maintenance: AgeStatusCount


class MaintenanceRecord(BaseModel):
    """Individual maintenance record."""
    maintenance_date: date
    maintenance_action: str
    notes: str
    anomaly_detected: bool | None = None


class OldestMachineMaintenance(BaseModel):
    """Maintenance history for one of the oldest machines."""
    machine_id: int
    machine_name: str
    location: str
    status: str
    installation_date: date
    age_years: float
    last_3_maintenance: list[MaintenanceRecord]


class AnalysisAndIntervention(BaseModel):
    """Analysis and intervention suggestion based on maintenance history."""
    analysis: str
    intervention_suggestion: str


class MachineAgeAnalysisResponse(BaseModel):
    """Response for query ops_l4_3."""
    analysis_date: date
    average_machine_age_by_status: AverageAgeByStatus
    recent_maintenance_for_oldest_maintenance_machines: list[OldestMachineMaintenance]
    analysis_and_intervention_suggestion: AnalysisAndIntervention

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MachineAgeAnalysisResponse):
            return NotImplemented
        return (
            self.analysis_date == other.analysis_date
            and self.average_machine_age_by_status == other.average_machine_age_by_status
            and len(self.recent_maintenance_for_oldest_maintenance_machines) == len(other.recent_maintenance_for_oldest_maintenance_machines)
            and are_strings_similar(self.analysis_and_intervention_suggestion.analysis, other.analysis_and_intervention_suggestion.analysis)
            and are_strings_similar(self.analysis_and_intervention_suggestion.intervention_suggestion, other.analysis_and_intervention_suggestion.intervention_suggestion)
        )