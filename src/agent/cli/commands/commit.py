"""Create git commits via the git tool adapter."""

import asyncio

import typer

from agent.tools.adapters import git as git_adapter


def main(
    message: str = typer.Option(..., "-m", "--message", help="Commit message"),
) -> None:
    """Commit staged changes with *message*."""

    result = asyncio.run(
        git_adapter.call({"command": "commit", "message": message})
    )
    if result["stdout"]:
        typer.echo(result["stdout"])
    if result["stderr"]:
        typer.echo(result["stderr"], err=True)
    raise typer.Exit(result["code"])
