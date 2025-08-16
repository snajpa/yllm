"""Main agent loop executing planner output."""

from __future__ import annotations

import asyncio
import json

from .planner import Planner
from .scheduler import execute_tool_calls_parallel, ready_batches
from ..tools.dispatch import to_call


async def run_turn(goal: str, repo_view: dict):
    """Plan and execute a single agent turn."""

    planner = Planner()
    plan_json = planner.forward(goal, repo_view)
    plan = json.loads(plan_json or "{}")
    steps = plan.get("steps", [])

    results = []
    for batch in ready_batches(steps):
        calls = [to_call(step) for step in batch]
        batch_results = await execute_tool_calls_parallel(calls)
        results.extend(batch_results)
    return results


def run_sync(goal: str, repo_view: dict):
    """Synchronously execute :func:`run_turn` for CLI usage."""

    return asyncio.run(run_turn(goal, repo_view))
