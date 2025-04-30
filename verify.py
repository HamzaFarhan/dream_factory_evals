import os

import httpx

BASE_URL = os.environ["DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["DREAM_FACTORY_FINANCE_API_KEY"]}

res = httpx.get(
    f"{BASE_URL}/_schema/finance_revenues",
    headers=HEADERS,
).json()

print(res)
