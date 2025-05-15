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

SCORES_DIR = Path("scores")
SCORES_DIR.mkdir(parents=True, exist_ok=True)


def save_scores(model: KnownModelName, user_role: Role, level: int) -> pd.DataFrame:
    report_name = f"{model.upper()}-{user_role.value.upper()}-LEVEL-{level}"
    scores_path = SCORES_DIR / f"{report_name}.csv"
    query = f"""
    SELECT r.created_at, r.start_timestamp, r.end_timestamp, r.duration, r.trace_id, r.attributes FROM records r 
    WHERE attributes->>'name' = '{report_name}'
    ORDER BY created_at DESC
    LIMIT 1;
    """

    with LogfireQueryClient(read_token=logfire_read_token) as client:
        json_report = client.query_json(sql=query)
        report = {col["name"]: {k: v for k, v in col.items() if k != "name"} for col in json_report["columns"]}
        (SCORES_DIR / f"{report_name}.json").write_text(json.dumps(report))

    cases = json.loads(Path(SCORES_DIR / f"{report_name}.json").read_text())["attributes"]["values"][0]["cases"]

    cases_metrics: list[dict[str, str | int | float]] = []
    for case in cases:
        accuracy = 2 * int(case["assertions"]["EvaluateResult"]["value"])
        correct_tool_calls = int(case["assertions"]["EvaluateToolCalls"]["value"])
        incorrect_tool_calls_reason = case["assertions"]["EvaluateToolCalls"]["reason"]
        score = accuracy + correct_tool_calls
        output = case["output"]
        expected_output = case["expected_output"]
        cases_metrics.append(
            {
                "name": case["name"],
                "model": model,
                "duration": case["task_duration"],
                "accuracy": accuracy,
                "expected_output": expected_output.get("result", expected_output.get("output", "")),
                "output": output.get("result", output.get("output", "")),
                "correct_tool_calls": correct_tool_calls,
                "incorrect_tool_calls_reason": incorrect_tool_calls_reason,
                "score": score,
            }
        )

    df = pd.DataFrame(cases_metrics)
    df.to_csv(scores_path, index=False)
    logger.success(f"Saved scores to {scores_path}")
    return df


def create_leaderboard(user_role: Role, level: int, models: list[KnownModelName]) -> None:
    """Create a leaderboard comparing all models for a specific role and level."""
    combined_df = pd.DataFrame()

    for model in models:
        model_df = save_scores(model=model, user_role=user_role, level=level)
        combined_df = pd.concat([combined_df, model_df])

    # Calculate aggregate metrics per model
    leaderboard = (
        combined_df.groupby("model")  # type: ignore
        .agg(
            avg_score=("score", "mean"),
            avg_accuracy=("accuracy", "mean"),
            avg_tool_calls=("correct_tool_calls", "mean"),
            avg_duration=("duration", "mean"),
            total_score=("score", "sum"),
            query_count=("name", "count"),
        )
        .reset_index()
    )

    # Sort by average score descending
    leaderboard = leaderboard.sort_values("avg_score", ascending=False)  # type: ignore

    # Save leaderboard
    leaderboard_path = Path("scores") / f"leaderboard_{user_role.value}_level{level}.csv"
    leaderboard.to_csv(leaderboard_path, index=False)
    logger.success(f"Created leaderboard at {leaderboard_path}")

    # Also save the full results with all queries for each model
    detailed_path = Path("scores") / f"detailed_{user_role.value}_level{level}.csv"
    combined_df.to_csv(detailed_path, index=False)
    logger.success(f"Saved detailed comparison at {detailed_path}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--user-role", type=str, required=True, choices=[r.value for r in Role])
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--leaderboard", action="store_true", help="Create leaderboard for all models")
    args = parser.parse_args()

    level = args.level
    user_role = Role(args.user_role.lower())

    if args.leaderboard:
        models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
        create_leaderboard(user_role=user_role, level=level, models=models)
    else:
        model = args.model
        save_scores(model=model, user_role=user_role, level=level)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-nano", "openai:gpt-4.1-mini"]
    # Create a leaderboard for HR role, level 1
    create_leaderboard(user_role=Role.HR, level=1, models=models)
