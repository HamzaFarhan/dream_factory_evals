import argparse
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient
from loguru import logger
from pydantic_ai.models import KnownModelName

from dream_factory_evals.df_agent import Role

load_dotenv()

logfire_read_token = os.getenv("LOGFIRE_READ_TOKEN", "")


def save_scores(model: KnownModelName, user_role: Role, level: int) -> None:
    report_name = f"{model.upper()}-{user_role.value.upper()}-LEVEL-{level}"
    scores_dir = Path("scores")
    scores_dir.mkdir(exist_ok=True)
    scores_path = scores_dir / f"{report_name}.csv"
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

    df = pd.DataFrame(cases_metrics)
    df.to_csv(scores_path, index=False)
    logger.success(f"Saved scores to {scores_path}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--user-role", type=str, required=True, choices=[r.value for r in Role])
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()

    level = args.level
    user_role = Role(args.user_role.lower())
    model = args.model

    save_scores(model=model, user_role=user_role, level=level)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    for model in models:
        save_scores(model=model, user_role=Role.HR, level=1)
