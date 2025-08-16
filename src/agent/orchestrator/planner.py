"""Deterministic planner returning a small example plan."""

import json
from typing import Dict


class Planner:
    """Return a static plan demonstrating the orchestrator flow."""

    def forward(self, goal: str, repo_view: Dict) -> str:  # noqa: D401
        plan = {
            "steps": [
                {
                    "id": "readme",
                    "kind": "read",
                    "deps": [],
                    "parallelizable": True,
                    "tool": "fs.read",
                    "args": {"path": "README.md"},
                },
                {
                    "id": "echo",
                    "kind": "run",
                    "deps": ["readme"],
                    "parallelizable": False,
                    "tool": "run",
                    "args": {"command": "echo done"},
                },
            ]
        }
        return json.dumps(plan)
