import os

import httpx

BASE_URL = os.environ["DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["DREAM_FACTORY_CEO_API_KEY"]}

res = httpx.get(
    f"{BASE_URL}/_table/ops_machines",
    headers=HEADERS,
    params={
        "filter": "(status = 'Active')",
        "fields": "machine_id,location,installation_date",
        "related": "ops_maintenance_by_machine_id",
    },
).json()

res

location_dict = {r["location"]: {"active_machines": 0, "anomalies": 0} for r in res["resource"]}
for r in res["resource"]:
    location_dict[r["location"]]["active_machines"] += 1
    location_dict[r["location"]]["anomalies"] += len(
        [m for m in r["ops_maintenance_by_machine_id"] if m["anomaly_detected"]]
    )

for location, data in location_dict.items():
    location_dict[location]["anomaly_rate"] = data["anomalies"] / data["active_machines"]

{
    "New York": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Chicago": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Phoenix": {"active_machines": 1, "anomalies": 1, "anomaly_rate": 1.0},
    "San Antonio": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "San Diego": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "San Jose": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Jacksonville": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Fort Worth": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Charlotte": {"active_machines": 1, "anomalies": 1, "anomaly_rate": 1.0},
    "Indianapolis": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Seattle": {"active_machines": 1, "anomalies": 0, "anomaly_rate": 0.0},
    "Washington": {"active_machines": 1, "anomalies": 1, "anomaly_rate": 1.0},
}
