"""Execute shell commands inside the sandbox."""

import asyncio
from typing import Any, Dict, Optional


async def call(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run ``command`` and capture its output."""

    args = args or {}
    command = args.get("command", "")
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {
        "code": proc.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
    }
