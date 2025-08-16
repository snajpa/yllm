"""Router module stub."""

import dspy
from .types import Step


class RouteSig(dspy.Signature):
    """Map a step to a concrete tool invocation."""
    step: dict
    returns: str


class Router(dspy.Module):
    def __init__(self):
        super().__init__()
        self.pred = dspy.Predict(RouteSig)

    def forward(self, step: Step):
        return self.pred(step=step).returns
