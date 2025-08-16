from agent.context.retriever import build_repo_view


def test_build_repo_view_includes_agents_md():
    view = build_repo_view()
    assert "AGENTS.md" in view
    assert "DSPy" in view["AGENTS.md"]
