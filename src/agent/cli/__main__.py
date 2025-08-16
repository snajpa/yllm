"""CLI entrypoint using Typer.

This exposes the ``plan`` command for now. When invoked via either
``python -m agent.cli`` or the ``agent`` console script, it will
dispatch to the Typer app defined here.
"""

import typer

from .commands import plan as plan_cmd
from .commands import llama as llama_cmd

app = typer.Typer(add_completion=False)
app.command("plan")(plan_cmd.main)
app.command("llama")(llama_cmd.main)


if __name__ == "__main__":
    app()


if __name__ == "__main__":
    app()
