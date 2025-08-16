"""CLI entrypoint using Typer."""

import typer

from .commands import plan as plan_cmd

app = typer.Typer(add_completion=False)
app.command()(plan_cmd.main)


if __name__ == "__main__":
    app()
