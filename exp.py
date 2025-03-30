import json
import os
from pathlib import Path

import httpx

BASE_URL = os.environ["DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["DREAM_FACTORY_CEO_API_KEY"]}
tables = httpx.get(f"{BASE_URL}/_table/", headers=HEADERS).json()["resource"]

for table in tables:
    print(table)
    res = httpx.get(f"{BASE_URL}/_table/{table['name']}/", headers=HEADERS).json()["resource"]
    Path(f"data/{table['name']}.json").write_text(json.dumps(res, indent=2))

