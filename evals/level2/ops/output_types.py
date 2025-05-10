from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


class MachineMaintenanceInfo(BaseModel):
    machine_name: str
    machine_status: str
    last_maintenance_date: date
    maintenance_action: str
    notes: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MachineMaintenanceInfo):
            return NotImplemented
        return (
            self.machine_name == other.machine_name
            and self.machine_status == other.machine_status
            and self.last_maintenance_date == other.last_maintenance_date
            and self.maintenance_action == other.maintenance_action
            and are_strings_similar(self.notes, other.notes)
        )


class MachineLocation(BaseModel):
    machine_name: str
    location: str


class MaintenanceStatusInfo(BaseModel):
    maintenance_count: int
    machines: list[MachineLocation]


class MaintenanceActionCount(BaseModel):
    routine_check_count: int
    replaced_part_count: int


class MachineAnomalyInfo(BaseModel):
    machine_name: str
    maintenance_date: date
    notes: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MachineAnomalyInfo):
            return NotImplemented
        return (
            self.machine_name == other.machine_name
            and self.maintenance_date == other.maintenance_date
            and are_strings_similar(self.notes, other.notes)
        )


class MachinesWithAnomalies(BaseModel):
    machines_with_anomalies: list[MachineAnomalyInfo]


class MachineAgeInfo(BaseModel):
    average_age_years: float
    active_machine_count: int
