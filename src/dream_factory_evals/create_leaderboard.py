import json
import os
from pathlib import Path

import pandas as pd
import typer
from dotenv import load_dotenv
from logfire.experimental.query_client import LogfireQueryClient
from loguru import logger

load_dotenv()

logfire_read_token = os.environ["LOGFIRE_READ_TOKEN"]

SCORES_DIR = Path(os.getenv("SCORES_DIR", "scores"))
SCORES_DIR.mkdir(parents=True, exist_ok=True)

app = typer.Typer()


def save_scores(report_name: str) -> pd.DataFrame:
    logger.info(f"Saving scores for {report_name}")
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
    report_values = json.loads(Path(SCORES_DIR / f"{report_name}.json").read_text())["attributes"]["values"][0]
    evaluation_name = report_values["name"]
    cases = report_values["cases"]

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
                "evaluation_name": evaluation_name,
                "case_name": case["name"],
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


@app.command()
def create(
    leaderboard_name: str = typer.Argument(help="Name for the leaderboard file"),
    report_names: list[str] = typer.Argument(help="List of report names to include in leaderboard"),
):
    """Create a leaderboard comparing models from multiple evaluation reports."""
    if not report_names:
        logger.error("At least one report name is required")
        raise typer.Exit(1)

    logger.info(f"Creating leaderboard '{leaderboard_name}' from reports: {', '.join(report_names)}")
    create_leaderboard(leaderboard_name=leaderboard_name, report_names=report_names)


def create_leaderboard(leaderboard_name: str, report_names: list[str]) -> None:
    """Create a leaderboard comparing all models for a specific role and level."""
    combined_df = pd.DataFrame()

    for report_name in report_names:
        try:
            model_df = save_scores(report_name)
            combined_df = pd.concat([combined_df, model_df])
        except Exception as e:
            logger.error(f"Error saving scores for {report_name}: {e}")
            continue
    try:
        leaderboard = (
            combined_df.groupby("evaluation_name")  # type: ignore
            .agg(
                avg_score=("score", "mean"),
                avg_accuracy=("accuracy", "mean"),
                avg_tool_calls=("correct_tool_calls", "mean"),
                avg_duration=("duration", "mean"),
                total_score=("score", "sum"),
                query_count=("case_name", "count"),
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
    except Exception as e:
        logger.error(f"Error creating leaderboard: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
