import argparse
import json
import os
from pathlib import Path

import polars as pl
from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient

from dream_factory_evals.df_agent import Role


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--domain", type=str, required=True, choices=[r.value for r in Role])
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()

    logfire_read_token = os.getenv("LOGFIRE_READ_TOKEN", "")
    level = args.level
    domain = args.domain.lower()
    model = args.model
    user_role = Role(domain)
    report_name = f"{model.upper()}-{user_role.value.upper()}-LEVEL-{level}"

    query = f"""
    SELECT r.created_at, r.start_timestamp, r.end_timestamp, r.duration, r.trace_id, r.attributes FROM records r 
    WHERE attributes->>'name' = '{report_name}'
    ORDER BY created_at DESC
    LIMIT 1;
    """

    with LogfireQueryClient(read_token=logfire_read_token) as client:
        json_report = client.query_json(sql=query)
        report = {col["name"]: {k: v for k, v in col.items() if k != "name"} for col in json_report["columns"]}
        Path(f"{report_name}.json").write_text(json.dumps(report))

    cases = json.loads(Path(f"{report_name}.json").read_text())["attributes"]["values"][0]["cases"]

    cases_metrics = []
    for case in cases:
        accuracy = 2 * int(case["assertions"]["EvaluateResult"]["value"])
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

    df = pl.DataFrame(cases_metrics)
    scores_dir = Path("scores")
    scores_dir.mkdir(exist_ok=True)
    out_path = scores_dir / f"{report_name}.parquet"
    df.write_parquet(out_path)
    print(f"Saved scores to {out_path}")
    print(df)


if __name__ == "__main__":
    main()
