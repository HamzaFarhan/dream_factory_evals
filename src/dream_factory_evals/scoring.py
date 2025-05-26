import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient
from loguru import logger
from pydantic_ai.models import KnownModelName

from dream_factory_evals.df_agent import ReportInfo, Role

load_dotenv()

logfire_read_token = os.getenv("LOGFIRE_READ_TOKEN", "")

SCORES_DIR = Path(os.getenv("SCORES_DIR", "scores"))
SCORES_DIR.mkdir(parents=True, exist_ok=True)


def save_scores(report_info: ReportInfo) -> pd.DataFrame:
    logger.info(f"Saving scores for {report_info.name}")
    scores_path = SCORES_DIR / f"{report_info.name}.csv"
    query = f"""
    SELECT r.created_at, r.start_timestamp, r.end_timestamp, r.duration, r.trace_id, r.attributes FROM records r 
    WHERE attributes->>'name' = '{report_info.name}'
    ORDER BY created_at DESC
    LIMIT 1;
    """

    with LogfireQueryClient(read_token=logfire_read_token) as client:
        json_report = client.query_json(sql=query)
        report = {col["name"]: {k: v for k, v in col.items() if k != "name"} for col in json_report["columns"]}
        (SCORES_DIR / f"{report_info.name}.json").write_text(json.dumps(report))

    cases = json.loads(Path(SCORES_DIR / f"{report_info.name}.json").read_text())["attributes"]["values"][0][
        "cases"
    ]

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
                "model": report_info.model,
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


def create_leaderboard(leaderboard_name: str, report_infos: list[ReportInfo]) -> None:
    """Create a leaderboard comparing all models for a specific role and level."""
    combined_df = pd.DataFrame()

    for report_info in report_infos:
        model_df = save_scores(report_info)
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
    leaderboard_path = Path("scores") / f"{leaderboard_name}.csv"
    leaderboard.to_csv(leaderboard_path, index=False)
    logger.success(f"Created leaderboard at {leaderboard_path}")

    # Also save the full results with all queries for each model
    detailed_path = Path("scores") / f"detailed_{leaderboard_name}.csv"
    combined_df.to_csv(detailed_path, index=False)
    logger.success(f"Saved detailed comparison at {detailed_path}")


if __name__ == "__main__":
    user_role = Role.HR
    level = 1
    models: list[KnownModelName] = ["openai:gpt-4o", "openai:gpt-4o-mini"]
    report_infos: list[ReportInfo] = [
        ReportInfo(name=f"{model}-{user_role.value}-level-{level}", model=model, user_role=user_role, level=level)
        for model in models
    ]
    # Create a leaderboard for HR role, level 1
    create_leaderboard(leaderboard_name=f"{user_role.value}-level-{level}", report_infos=report_infos)
