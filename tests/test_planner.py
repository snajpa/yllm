import json

from agent.orchestrator.planner import Planner


def test_planner_returns_plan():
    plan_json = Planner().forward("demo", {})
    plan = json.loads(plan_json)
    assert "steps" in plan
    assert len(plan["steps"]) == 2
