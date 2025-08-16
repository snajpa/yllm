"""Test runner adapter."""

from typing import Any, Dict, Optional

from .run import call as run_call


async def call(args: Optional[Dict[str, Any]] = None) -> Any:
    """Run the project's tests using the run adapter."""

    args = args or {}
    command = args.get("command", "pytest -q")
    return await run_call({"command": command})
