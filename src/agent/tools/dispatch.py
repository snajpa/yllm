"""Dispatch utilities for tool adapters."""
from typing import Any, Callable, Dict

from ..orchestrator.types import Step, ToolCall
from .adapters import files, run, test

_ADAPTERS: Dict[str, Callable[[Dict[str, Any]], Any]] = {
    "fs.read": files.call,
    "run": run.call,
    "test": test.call,
}


def resolve_tool(name: str) -> Callable[[Dict[str, Any]], Any]:
    """Return the callable adapter for *name*.

    Parameters
    ----------
    name: str
        Logical tool name as it appears in a Plan step.
    """
    return _ADAPTERS[name]


def to_call(step: Step) -> ToolCall:
    """Convert a :class:`Step` into a :class:`ToolCall`."""
    return {"id": step["id"], "name": step["tool"], "args": step.get("args", {})}
