import json
import os
from pathlib import Path

import httpx

schema_path = Path("./new_data/schema.json")

BASE_URL = os.environ["NEW_DREAM_FACTORY_BASE_URL"]

HEADERS = {"X-DreamFactory-API-Key": os.environ["NEW_DREAM_FACTORY_CEO_API_KEY"]}
all_tables = httpx.get(f"{BASE_URL}/_schema", headers=HEADERS).json()
for table in all_tables["resource"]:
    schema = json.loads(schema_path.read_text()) if schema_path.exists() else {}
    res = httpx.get(f"{BASE_URL}/_schema/{table['name']}", headers=HEADERS).json()
    schema[table["name"]] = res
    schema_path.write_text(json.dumps(schema, indent=2))
