"""Minimal git tool adapter."""

import asyncio
from typing import Any, Dict, Optional


async def call(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run simple git commands and capture their output.

    Supported commands:

    - ``commit`` – create a commit with the provided message using
      ``git commit -am``.
    """

    args = args or {}
    command = args.get("command")

    if command == "commit":
        message = args.get("message", "")
        proc = await asyncio.create_subprocess_exec(
            "git",
            "commit",
            "-am",
            message,
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
