"""CLI entrypoint using Typer."""

import typer

from agent.orchestrator.runtime import run_sync

app = typer.Typer(add_completion=False)


@app.command()
def plan(goal: str):
    """Plan and execute a simple workflow for *goal*."""

    results = run_sync(goal, {})
    typer.echo(results)


if __name__ == "__main__":
    app()
