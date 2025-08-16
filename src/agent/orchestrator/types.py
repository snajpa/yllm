"""Type definitions for orchestrator."""

from typing import TypedDict, List, Dict, Any, Optional, Literal


class ToolCall(TypedDict):
    name: str
    id: str
    args: Dict[str, Any]


class ToolResult(TypedDict):
    id: str
    name: str
    ok: bool
    output: Any
    error: Optional[str]


class Step(TypedDict):
    id: str
    kind: Literal["read", "search", "edit", "patch", "run", "test", "explain"]
    deps: List[str]
    parallelizable: bool
    tool: str
    args: Dict[str, Any]


class Plan(TypedDict):
    steps: List[Step]
