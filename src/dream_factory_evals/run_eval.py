#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import get_args

import typer
from dotenv import load_dotenv
from loguru import logger
from pydantic_ai.models import KnownModelName

from dream_factory_evals.df_agent import ReportInfo, Role, TaskConfig, evaluate

load_dotenv()

PROMPT_NAME = os.getenv("PROMPT_NAME", "basic_prompt.txt")
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "20"))
RETRIES = int(os.getenv("RETRIES", "3"))

app = typer.Typer()


# Get valid model names from ModelT type
def get_valid_models() -> list[str]:
    """Get all valid model names from ModelT type."""
    known_models = [
        m
        for m in list(get_args(KnownModelName.__value__))
        if any(m.startswith(x) for x in ["anthropic", "google", "openai"])
    ]
    literal_models = ["SG_LANG", "Qwen2.5"]
    return known_models + literal_models


def get_valid_roles() -> list[str]:
    """Get all valid role values."""
    return [role.value for role in Role]


@app.command()
def run(
    model: str = typer.Argument(
        help="Model name to use for evaluation. Examples: openai:gpt-4.1-mini, anthropic:claude-4-sonnet-20250514, google-gla:gemini-2.0-flash"
    ),
    role: str = typer.Argument(help="User role for evaluation"),
    level: int = typer.Argument(help="Evaluation level (1-4)"),
    report_name: str | None = typer.Option(None, help="Report name (defaults to model-role-level-N)"),
    prompt_name: str = typer.Option(PROMPT_NAME, help="Prompt file to use"),
    max_tool_calls: int = typer.Option(MAX_TOOL_CALLS, help="Maximum number of tool calls"),
    retries: int = typer.Option(RETRIES, help="Number of retries on failure"),
):
    """Run evaluations for a specific model, role, and level."""

    # Validate inputs
    valid_models = get_valid_models()
    if model not in valid_models:
        logger.error(f"Invalid model: {model}. Valid models: {', '.join(valid_models)}")
        raise typer.Exit(1)

    valid_roles = get_valid_roles()
    if role not in valid_roles:
        logger.error(f"Invalid role: {role}. Valid roles: {', '.join(valid_roles)}")
        raise typer.Exit(1)

    if level not in [1, 2, 3, 4]:
        logger.error(f"Invalid level: {level}. Valid levels: 1, 2, 3, 4")
        raise typer.Exit(1)

    # Run evaluation
    asyncio.run(_run_evaluation(model, role, level, report_name, prompt_name, max_tool_calls, retries))


async def _run_evaluation(
    model: str,
    role: str,
    level: int,
    report_name: str | None,
    prompt_name: str,
    max_tool_calls: int,
    retries: int,
):
    """Run the actual evaluation."""
    # Dynamic import of the dataset
    module_path = f"evals.level{level}.{role}.evals"
    dataset_name = f"{role}_dataset"

    try:
        logger.info(f"Importing {dataset_name} from {module_path}")

        # Add project root to Python path so we can import from evals
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        module = importlib.import_module(module_path)
        dataset = getattr(module, dataset_name)

        # Convert role string to Role enum
        user_role = Role(role)

        # Create task config
        task_config = TaskConfig(
            user_role=user_role,
            model=model,  # type: ignore
            prompt_name=prompt_name,
            max_tool_calls=max_tool_calls,
            retries=retries,
        )

        # Create report info
        final_report_name = report_name or f"{model}-{user_role.value}-level-{level}"
        report_info = ReportInfo(
            name=final_report_name,
            model=model,  # type: ignore
            user_role=user_role,
            level=level,
        )

        # Run evaluation
        logger.info(f"Running evaluation: {report_info.name}")
        _ = await evaluate(report_info=report_info, dataset=dataset, task_config=task_config)

        logger.success(f"Evaluation completed successfully: {report_info.name}")

    except ImportError as e:
        logger.error(f"Failed to import dataset from {module_path}: {e}")
        logger.error(f"Make sure the dataset exists at evals/level{level}/{role}/evals.py")
        raise typer.Exit(1)
    except AttributeError as e:
        logger.error(f"Dataset '{dataset_name}' not found in module {module_path}: {e}")
        raise typer.Exit(1)
    except Exception:
        logger.exception("Evaluation failed")
        raise typer.Exit(1)


@app.command()
def list_models():
    """List all available models."""
    models = get_valid_models()
    typer.echo("Available models:")
    for model in sorted(models):
        typer.echo(f"  - {model}")

    typer.echo("\nCommon examples:")
    typer.echo("  - openai:gpt-4.1-mini")
    typer.echo("  - anthropic:claude-4-sonnet-20250514")
    typer.echo("  - google-gla:gemini-2.0-flash")


@app.command()
def list_roles():
    """List all available roles."""
    roles = get_valid_roles()
    typer.echo("Available roles:")
    for role in roles:
        typer.echo(f"  - {role}")


if __name__ == "__main__":
    app()
