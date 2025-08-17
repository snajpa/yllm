"""Create git commits via the git tool adapter."""

import asyncio

import typer

from agent.tools.adapters import git as git_adapter


def main(
    message: str = typer.Option(..., "-m", "--message", help="Commit message"),
    all: bool = typer.Option(
        False,
        "-a",
        "--all",
        help="Commit all tracked changes, not just staged ones",
    ),
) -> None:
    """Commit changes with *message*.

    By default only staged files are committed. Use ``--all`` to include
    all tracked modifications.
    """

    result = asyncio.run(
        git_adapter.call({"command": "commit", "message": message, "all": all})
    )
    if result["stdout"]:
        typer.echo(result["stdout"])
    if result["stderr"]:
        typer.echo(result["stderr"], err=True)
    raise typer.Exit(result["code"])
