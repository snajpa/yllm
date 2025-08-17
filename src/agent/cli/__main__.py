"""CLI entrypoint using Typer.

This module wires up the available subcommands and exposes them through the
``agent`` console script or ``python -m agent.cli``.
"""

import typer

from .commands import llama as llama_cmd
from .commands import plan as plan_cmd
from .commands import run as run_cmd
from .commands import test as test_cmd
from .commands import commit as commit_cmd

app = typer.Typer(add_completion=False)
app.command("plan")(plan_cmd.main)
app.command("llama")(llama_cmd.main)
app.command("run")(run_cmd.main)
app.command("test")(test_cmd.main)
app.command("commit")(commit_cmd.main)


if __name__ == "__main__":
    app()
