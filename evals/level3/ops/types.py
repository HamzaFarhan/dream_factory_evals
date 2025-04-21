from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]

class MaintenanceByLocation(BaseModel):
    maintenance_by_location: dict[str, int]

class AnomalyRate(BaseModel):
    location: str
    anomaly_rate: float

class AnomalyRates(BaseModel):
    anomaly_rates: list[AnomalyRate]

class InstallationYearComparisonItem(BaseModel):
    total_machines: int
    machines_with_maintenance: int
    avg_days_to_first_maintenance: float

class InstallationYearComparison(BaseModel):
    installation_year_comparison: dict[str, InstallationYearComparisonItem]
    insight: str
