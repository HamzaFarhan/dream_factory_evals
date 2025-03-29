import os

import httpx

BASE_URL = os.environ["DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["DREAM_FACTORY_HR_API_KEY"]}

res = httpx.get(f"{BASE_URL}/_table/", headers=HEADERS).json()
res

