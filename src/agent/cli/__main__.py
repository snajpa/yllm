"""CLI entrypoint using Typer."""

import typer

app = typer.Typer(add_completion=False)


@app.command()
def plan(goal: str):
    """Plan code changes (stub)."""
    typer.echo(f"planning: {goal}")


if __name__ == "__main__":
    app()
