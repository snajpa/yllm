"""Critic module stub."""

import dspy


class CriticSig(dspy.Signature):
    steps: list
    results: list
    repo_state: dict
    score: float
    feedback: str


class Critic(dspy.Module):
    def __init__(self):
        super().__init__()
        self.pred = dspy.Predict(CriticSig)

    def forward(self, steps, results, repo_state):
        return self.pred(steps=steps, results=results, repo_state=repo_state)
