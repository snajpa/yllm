"""Execute shell commands via the run tool adapter."""

import asyncio

import typer

from agent.tools.adapters import run as run_adapter


def main(command: str) -> None:
    """Run *command* inside the sandbox and stream its output."""

    result = asyncio.run(run_adapter.call({"command": command}))
    if result["stdout"]:
        typer.echo(result["stdout"])
    if result["stderr"]:
        typer.echo(result["stderr"], err=True)
    raise typer.Exit(result["code"])
