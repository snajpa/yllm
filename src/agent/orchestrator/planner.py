"""Planner module stub."""

import dspy


class PlanSig(dspy.Signature):
    """Plan code changes and checks as a DAG."""
    goal: str
    repo_view: dict
    returns: str


class Planner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.pred = dspy.ChainOfThought(PlanSig)

    def forward(self, goal: str, repo_view: dict) -> str:
        return self.pred(goal=goal, repo_view=repo_view).returns
