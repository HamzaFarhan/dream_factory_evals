import os

import httpx

BASE_URL = os.environ["NEW_DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["NEW_DREAM_FACTORY_CEO_API_KEY"]}

res = httpx.get(f"{BASE_URL}/_table", headers=HEADERS).json()

res
