"""Plan command implementation."""

from typing import Dict

import typer

from agent.context.retriever import build_repo_view
from agent.orchestrator.runtime import run_sync


def main(goal: str) -> None:
    """Generate and execute a plan for *goal* and echo the results."""

    repo_view: Dict[str, str] = build_repo_view()
    results = run_sync(goal, repo_view)
    typer.echo(results)
