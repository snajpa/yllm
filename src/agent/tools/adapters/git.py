"""Minimal git tool adapter."""

import asyncio
from typing import Any, Dict, Optional


async def call(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run simple git commands and capture their output.

    Supported commands:

    - ``commit`` – create a commit with the provided message. When
      ``all`` is set, this runs ``git commit -am`` to include tracked
      changes; otherwise only staged files are committed with
      ``git commit -m``.
    """

    args = args or {}
    command = args.get("command")

    if command == "commit":
        message = args.get("message", "")
        commit_args = ["git", "commit"]
        if args.get("all"):
            commit_args.append("-am")
            commit_args.append(message)
        else:
            commit_args.extend(["-m", message])
        proc = await asyncio.create_subprocess_exec(
            *commit_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    else:
        raise ValueError("unsupported git command")

    stdout, stderr = await proc.communicate()
    return {
        "code": proc.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
    }
