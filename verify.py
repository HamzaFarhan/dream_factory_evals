import os
from datetime import datetime

import httpx

BASE_URL = os.environ["DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["DREAM_FACTORY_CEO_API_KEY"]}

res = httpx.get(
    f"{BASE_URL}/_table/hr_employees",
    headers=HEADERS,
    params={
        "fields": "employee_id, date_joined, department_id",
        "filter": "(role='Manager') AND (date_joined >= '2022-01-01') AND (date_joined <= '2023-12-31')",
        "related": "hr_departments_by_department_id",
    },
).json()

res2 = httpx.get(
    f"{BASE_URL}/_table/hr_policies",
    headers=HEADERS,
    params={
        "fields": "policy_id, effective_date, department_id",
        "filter": "department_id IN (3, 5, 8, 11, 14, 17, 20) AND (effective_date >= '2022-01-01') AND (effective_date <= '2023-12-31')",
    },
).json()

department_timing_analysis = []

# Create mapping of department_id to policy dates
policy_dates = {}
for policy in res2["resource"]:
    dept_id = policy["department_id"]
    date = policy["effective_date"]
    if dept_id not in policy_dates or date < policy_dates[dept_id]:
        policy_dates[dept_id] = date

# Create mapping of department_id to manager join dates
manager_dates = {}
for emp in res["resource"]:
    dept_id = emp["department_id"]
    date = emp["date_joined"]
    dept_name = emp["hr_departments_by_department_id"]["name"]
    if dept_id not in manager_dates:
        manager_dates[dept_id] = (date, dept_name)

# Calculate timing analysis for each department
total_days = 0
count = 0
for dept_id, policy_date in policy_dates.items():
    if dept_id in manager_dates:
        manager_date, dept_name = manager_dates[dept_id]
        days_diff = (datetime.strptime(manager_date, "%Y-%m-%d") - datetime.strptime(policy_date, "%Y-%m-%d")).days
        total_days += days_diff
        count += 1

        department_timing_analysis.append(
            {
                "department_name": dept_name,
                "policy_date": policy_date,
                "manager_joined_date": manager_date,
                "days_difference": days_diff,
                "timing_pattern": "Manager joined after policy implementation",
            }
        )

average_days = total_days / count if count > 0 else 0
department_timing_analysis
average_days