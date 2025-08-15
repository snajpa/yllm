from agent.tools.dispatch import resolve_tool
from agent.tools.adapters import run


def test_resolve_tool_returns_adapter():
    assert resolve_tool("run") is run.call
