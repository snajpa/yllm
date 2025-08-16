"""Simple parallel scheduler for tool calls."""

from __future__ import annotations

import asyncio
from typing import Iterable, List

from .types import Step, ToolCall
from ..tools.dispatch import resolve_tool


def ready_batches(steps: List[Step]) -> Iterable[List[Step]]:
    """Yield batches of steps that can run in parallel."""

    remaining = {s["id"]: s for s in steps}
    completed: set[str] = set()
    while remaining:
        batch = [s for s in remaining.values() if set(s["deps"]).issubset(completed)]
        if not batch:
            break
        parallel = [s for s in batch if s.get("parallelizable", False)]
        sequential = [s for s in batch if not s.get("parallelizable", False)]
        if parallel:
            yield parallel
        for s in sequential:
            yield [s]
        for s in batch:
            completed.add(s["id"])
            remaining.pop(s["id"], None)


async def execute_tool_calls_parallel(calls: List[ToolCall]):
    """Execute tool calls concurrently."""

    tasks = [asyncio.create_task(invoke_call(c)) for c in calls]
    return await asyncio.gather(*tasks)


async def invoke_call(call: ToolCall):
    """Resolve and invoke a tool adapter."""

    fn = resolve_tool(call["name"])
    output = await fn(call.get("args", {}))
    return {"id": call["id"], "name": call["name"], "ok": True, "output": output, "error": None}
