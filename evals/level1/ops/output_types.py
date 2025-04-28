from typing import Annotated

from pydantic import BaseModel, Field

date = Annotated[str, Field(description="format: YYYY-MM-DD")]


class ActiveMachines(BaseModel):
    active_machines: int


class MachineStatus(BaseModel):
    machine_name: str
    status: str


class Machine(BaseModel):
    machine_id: int
    machine_name: str
    location: str


class Machines(BaseModel):
    machines: list[Machine]


class ReplacementCount(BaseModel):
    replacement_count: int
