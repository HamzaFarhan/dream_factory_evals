import os
from datetime import datetime

import httpx

BASE_URL = os.environ["DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["DREAM_FACTORY_CEO_API_KEY"]}

res = httpx.get(
    f"{BASE_URL}/_table/ops_machines",
    headers=HEADERS,
    params={
        "filter": "(installation_date >= '2021-01-01') AND (installation_date <= '2021-12-31')",
        "fields": "machine_id, installation_date",
        "related": "ops_maintenance_by_machine_id",
    },
).json()

res2 = httpx.get(
    f"{BASE_URL}/_table/ops_machines",
    headers=HEADERS,
    params={
        "filter": "(installation_date >= '2022-01-01') AND (installation_date <= '2022-12-31')",
        "related": "ops_maintenance_by_machine_id",
        "fields": "machine_id, installation_date",
    },
).json()


total_machines_2021 = len(res["resource"])
machines_with_maintenance_2021 = len([m for m in res["resource"] if m["ops_maintenance_by_machine_id"]])
days_between_maintenance_2021 = sum(
    [
        (
            datetime.strptime(m["ops_maintenance_by_machine_id"][0]["maintenance_date"], "%Y-%m-%d")
            - datetime.strptime(m["installation_date"], "%Y-%m-%d")
        ).days
        for m in res["resource"]
        if m["ops_maintenance_by_machine_id"]
    ]
)

print(f"Total machines in 2021: {total_machines_2021}")
print(f"Machines with maintenance in 2021: {machines_with_maintenance_2021}")
print(
    f"Average days between maintenance in 2021: {days_between_maintenance_2021 / machines_with_maintenance_2021}"
)

total_machines_2022 = len(res2["resource"])
machines_with_maintenance_2022 = len([m for m in res2["resource"] if m["ops_maintenance_by_machine_id"]])
days_between_maintenance_2022 = sum(
    [
        (
            datetime.strptime(m["ops_maintenance_by_machine_id"][0]["maintenance_date"], "%Y-%m-%d")
            - datetime.strptime(m["installation_date"], "%Y-%m-%d")
        ).days
        for m in res2["resource"]
        if m["ops_maintenance_by_machine_id"]
    ]
)

print(f"Total machines in 2022: {total_machines_2022}")
print(f"Machines with maintenance in 2022: {machines_with_maintenance_2022}")
print(
    f"Average days between maintenance in 2022: {days_between_maintenance_2022 / machines_with_maintenance_2022}"
)
