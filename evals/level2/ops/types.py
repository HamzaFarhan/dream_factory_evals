from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


class MachineMaintenanceInfo(BaseModel):
    machine_name: str
    machine_status: str
    last_maintenance_date: date
    maintenance_action: str
    notes: str


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


class MachinesWithAnomalies(BaseModel):
    machines_with_anomalies: list[MachineAnomalyInfo]


class MachineAgeInfo(BaseModel):
    average_age_years: float
    active_machine_count: int
