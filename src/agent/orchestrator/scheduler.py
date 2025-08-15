"""Parallel scheduler stub."""

import asyncio
from .types import Step, Plan


async def execute_tool_calls_parallel(calls):
    return await asyncio.gather(*calls)
