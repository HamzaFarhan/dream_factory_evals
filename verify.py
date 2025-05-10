import os

import httpx

BASE_URL = os.environ["NEW_DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["NEW_DREAM_FACTORY_HR_API_KEY"]}

res = httpx.get(
    f"{BASE_URL}/_table/hr_employees",
    headers=HEADERS,
    params={
        # "filter": "(department_id=3) AND (date_joined >= '2023-01-01') AND (date_joined <= '2023-12-31')",
        # "filter": "department_id=3",
        # "fields": "employee_id,first_name,last_name,role,date_joined",
        "related": "hr_departments_by_department_id",
        "limit": 20,
        "offset": 20,
    },
).json()

res
