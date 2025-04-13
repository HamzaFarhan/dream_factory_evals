import json
import os
from pathlib import Path

import polars as pl
from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient

from dream_factory_evals.df_agent import Role

load_dotenv()

LOGFIRE_READ_TOKEN = os.getenv("LOGFIRE_READ_TOKEN", "")
MODEL = "openai:gpt-4o-mini"
USER_ROLE = Role.HR
QUERY_LEVEL = 1
REPORT_NAME = f"{MODEL.upper()}-{USER_ROLE.value.upper()}-LEVEL-{QUERY_LEVEL}"

QUERY = f"""\
SELECT r.created_at, r.start_timestamp, r.end_timestamp, r.duration, r.trace_id, r.attributes FROM records r 
WHERE attributes->>'name' = '{REPORT_NAME}'
ORDER BY created_at DESC
LIMIT 1;
"""


with LogfireQueryClient(read_token=LOGFIRE_READ_TOKEN) as client:
    json_report = client.query_json(sql=QUERY)
    report = {col["name"]: {k: v for k, v in col.items() if k != "name"} for col in json_report["columns"]}
    Path(f"{REPORT_NAME}.json").write_text(json.dumps(report))


cases = json.loads(Path(f"{REPORT_NAME}.json").read_text())["attributes"]["values"][0]["cases"]


cases_metrics = []
for case in cases:
    accuracy = 2 * (int(case["assertions"]["EvaluateResult"]["value"]))
    correct_tool_calls = int(case["assertions"]["EvaluateToolCalls"]["value"])
    incorrect_tool_calls_reason = case["assertions"]["EvaluateToolCalls"]["reason"]
    score = accuracy + correct_tool_calls
    cases_metrics.append(
        {
            "name": case["name"],
            "duration": case["task_duration"],
            "accuracy": accuracy,
            "correct_tool_calls": correct_tool_calls,
            "incorrect_tool_calls_reason": incorrect_tool_calls_reason,
            "score": score,
        }
    )

print(pl.DataFrame(cases_metrics))
