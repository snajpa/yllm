"""Filesystem adapter with basic read/write support."""

from pathlib import Path
from typing import Any, Dict, Optional


async def call(args: Optional[Dict[str, Any]] = None) -> Any:
    """Execute a filesystem operation.

    Supported operations:
    - ``mode='r'``: read the file at ``path`` and return its contents.
    - ``mode='w'``: write ``content`` to ``path`` and return ``"ok"``.
    """

    args = args or {}
    path = Path(args["path"])
    mode = args.get("mode", "r")

    if mode == "r":
        return path.read_text()
    if mode == "w":
        content = args.get("content", "")
        path.write_text(content)
        return "ok"

    raise ValueError(f"Unsupported mode: {mode}")
