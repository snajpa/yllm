"""Run the project's tests via the test tool adapter."""

import asyncio

import typer

from agent.tools.adapters import test as test_adapter


def main(command: str = "pytest -q") -> None:
    """Execute the test ``command`` and echo its output."""

    result = asyncio.run(test_adapter.call({"command": command}))
    if result["stdout"]:
        typer.echo(result["stdout"])
    if result["stderr"]:
        typer.echo(result["stderr"], err=True)
    raise typer.Exit(result["code"])
