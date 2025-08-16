"""Simple llama.cpp completion demo command."""

import os
from typing import Optional

import typer

from agent.models.providers.llama_cpp import call as llama_call


def main(prompt: str, base_url: Optional[str] = typer.Option(None, help="Override LLAMA_CPP_BASE_URL")) -> None:
    """Send PROMPT to a llama.cpp server and print the completion."""

    # If provided, set env for child calls and pass directly as well
    if base_url:
        os.environ["LLAMA_CPP_BASE_URL"] = base_url
    out = llama_call(prompt, base_url=base_url)
    typer.echo(out)

