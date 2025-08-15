"""Main agent loop stub."""

from .planner import Planner
from .router import Router


def run_turn(goal: str, repo_view: dict):
    planner = Planner()
    router = Router()
    planner.forward(goal, repo_view)
    router.forward({})
    return {}
