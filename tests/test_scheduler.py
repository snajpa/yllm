from agent.orchestrator.scheduler import ready_batches


def test_ready_batches_groups_parallel_steps():
    steps = [
        {"id": "a", "deps": [], "parallelizable": True},
        {"id": "b", "deps": [], "parallelizable": True},
        {"id": "c", "deps": ["a", "b"], "parallelizable": False},
    ]
    batches = list(ready_batches(steps))
    assert len(batches) == 2
    assert {s["id"] for s in batches[0]} == {"a", "b"}
    assert [s["id"] for s in batches[1]] == ["c"]
