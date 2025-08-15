Open, DSPy-powered code assistant – a Codex-CLI / Claude-Code–style developer agent with parallel tool calling, MCP-first tooling, repo-aware Code-RAG, sandboxed execution, and policy enforcement.

0) TL;DR (10-km view)
CLI/TUI  ──► Agent Orchestrator (DSPy Program)
           ├─ Planner ─► DAG ─► Parallel Scheduler
           ├─ Tool Router (MCP + native adapters)
           ├─ Critics (tests/lints/spec) with BestOfN/Refine
           ├─ State: conversation, scratchpad, working tree diffs
           ├─ Context Engine (RepoGraph: AST/LSP/embeddings)
           ├─ Model Router (code vs. general reasoning)
           ├─ Execution/Safety (sandbox + OPA policy + budgets)
           └─ Observability/Evals (tracing, SWE-bench hooks)
                └─ Persistence: vector index + run artifacts


Parallel tool calling is supported two ways:

Model-native parallel tool calls (single turn emits multiple tool invocations).

Runtime-enforced parallelism via the Planner → DAG → Parallel Scheduler, even if the model can only call one tool at a time.

1) Repository layout (everything here should exist)

Paths under src/agent/** are importable Python modules. Create empty __init__.py files where needed.

.
├─ AGENTS.md                      # This file
├─ README.md
├─ LICENSE
├─ pyproject.toml                 # Python packaging + deps
├─ Makefile                       # dev shortcuts
├─ .env.example                   # env vars template
├─ .pre-commit-config.yaml
├─ scripts/
│  ├─ bootstrap_repo.sh           # create required dirs/files
│  ├─ index_repo.py               # one-off (re)index
│  ├─ run_eval.sh                 # run SWE-bench or custom evals
│  └─ demo.sh                     # end-to-end demo
├─ examples/
│  └─ hello_world_repo/           # tiny sample repo for demos
├─ tests/
│  ├─ test_planner.py
│  ├─ test_scheduler.py
│  ├─ test_router.py
│  └─ test_context.py
└─ src/
   └─ agent/
      ├─ __init__.py
      ├─ cli/
      │  ├─ __init__.py
      │  └─ __main__.py           # entrypoint (typer/rich)
      │     # subcommands implemented as functions here or in:
      │     └─ commands/
      │        ├─ plan.py         # /plan
      │        ├─ ctx.py          # /ctx
      │        ├─ edit.py         # /edit (propose patch)
      │        ├─ diff.py         # /diff
      │        ├─ apply.py        # /apply
      │        ├─ run.py          # /run
      │        ├─ test.py         # /test
      │        ├─ commit.py       # /commit
      │        └─ pr.py           # /pr
      ├─ orchestrator/
      │  ├─ __init__.py
      │  ├─ types.py              # ToolCall/Result, Plan/Step
      │  ├─ planner.py            # DSPy module (PlanSig)
      │  ├─ router.py             # DSPy+rules to choose tools
      │  ├─ scheduler.py          # Parallel executor (asyncio/Ray)
      │  ├─ critic.py             # BestOfN/Refine + reward fns
      │  ├─ runtime.py            # main agent loop
      │  └─ messages.py           # turn state & transcripts
      ├─ context/
      │  ├─ __init__.py
      │  ├─ indexer.py            # Tree-sitter/LSP ingestion
      │  ├─ repo_graph.py         # symbols/refs/edges
      │  ├─ retriever.py          # context pack assembly
      │  └─ embeddings.py         # vector store interface
      ├─ tools/
      │  ├─ __init__.py
      │  ├─ mcp_client.py         # Model Context Protocol client
      │  ├─ adapters/             # native Python tool adapters
      │  │  ├─ __init__.py
      │  │  ├─ files.py           # read/write, guarded
      │  │  ├─ git.py             # status/diff/commit/push
      │  │  ├─ run.py             # sandboxed run (unit cmd)
      │  │  ├─ test.py            # test runner harness
      │  │  ├─ search.py          # code search/grep
      │  │  ├─ browser.py         # http fetch (read-only by default)
      │  │  └─ docker.py          # build/run images (optional)
      │  └─ schemas/
      │     ├─ tool_base.py       # pydantic Tool schema
      │     └─ tool_specs/        # JSON Schemas (if needed)
      ├─ models/
      │  ├─ __init__.py
      │  ├─ router.py             # pick model per step
      │  ├─ interfaces.py         # LLM client interface
      │  └─ providers/
      │     ├─ openai.py          # optional
      │     ├─ anthropic.py       # optional
      │     ├─ vllm_open_weights.py# local/open models via vLLM
      │     └─ llama_cpp.py       # local/gguf (optional)
      ├─ runner/
      │  ├─ __init__.py
      │  ├─ sandbox.py            # gVisor/Firejail/Docker wrapper
      │  ├─ seccomp/
      │  │  └─ default.json
      │  └─ gvisor/
      │     └─ runsc_profile.json
      ├─ policy/
      │  ├─ __init__.py
      │  ├─ gate.py               # central allow/deny gate
      │  ├─ opa_client.py         # Rego decision requests
      │  └─ opa_policies/
      │     ├─ README.md
      │     └─ policy.rego
      ├─ observability/
      │  ├─ __init__.py
      │  ├─ tracing.py            # OpenTelemetry/OTLP
      │  ├─ metrics.py            # counters/timers
      │  └─ logging.py
      ├─ evals/
      │  ├─ __init__.py
      │  ├─ swebench.py           # harness glue (optional)
      │  └─ reward_functions.py   # lints/tests/specs -> score
      └─ config/
         ├─ __init__.py
         ├─ models.yaml           # default model routing
         ├─ tools.yaml            # MCP servers + adapters
         ├─ limits.yaml           # budgets/quotas
         ├─ sandbox.yaml          # runner defaults
         ├─ retrieval.yaml        # embedding + retriever params
         └─ mcp/
            └─ clients.json       # MCP client endpoints


All of the above must exist (empty files are fine for initial commit).

2) Installation & prerequisites

Python: 3.10+

System: Linux/macOS (Windows WSL recommended)

Recommended: uv or pipx, pre-commit, Docker (optional), gVisor or Firejail (for sandboxing)

# Create venv and install
uv venv && source .venv/bin/activate    # or python -m venv .venv
uv pip install -e .                     # or pip install -e .

# Setup pre-commit
pre-commit install

# Copy env template
cp .env.example .env && $EDITOR .env

# Create required directories and placeholder files
bash scripts/bootstrap_repo.sh


pyproject.toml should include (sketch): dspy-ai, pydantic, typer, rich, networkx, tree_sitter, opentelemetry-sdk, faiss-cpu (or chromadb), uvloop (posix), and provider SDKs you use.

3) Configuration files (required)

src/agent/config/models.yaml – model routing & providers.

src/agent/config/tools.yaml – list MCP servers and native adapters.

src/agent/config/limits.yaml – token/time budgets, parallelism caps.

src/agent/config/sandbox.yaml – default sandbox engine & profile.

src/agent/config/retrieval.yaml – embedding model + retriever knobs.

src/agent/config/mcp/clients.json – MCP endpoints & tool manifests.

.env – API keys, paths, feature flags (never commit real secrets).

Sample models.yaml:

default:
  reasoning: provider: anthropic  # or openai/local
  coding: provider: open_weights  # e.g., vllm qwen2.5-coder
providers:
  openai:
    model: gpt-4.1-mini
    parallel_tool_calls: true
    api_key_env: OPENAI_API_KEY
  anthropic:
    model: claude-3.7-sonnet
    parallel_tool_calls: true
    api_key_env: ANTHROPIC_API_KEY
  open_weights:
    endpoint: http://localhost:8000/v1
    model: qwen2.5-coder-32b-instruct
    parallel_tool_calls: false
routing_rules:
  - when: step.kind in ["edit","patch","generate_tests"]
    use: coding
  - when: step.kind in ["plan","explain","reason"]
    use: reasoning


Sample tools.yaml (hybrid MCP + native):

mcp:
  - name: fs
    endpoint: http://localhost:7331  # MCP Filesystem server
  - name: git
    endpoint: http://localhost:7332
  - name: fetch
    endpoint: http://localhost:7333
native:
  - name: run
    module: agent.tools.adapters.run:RunTool
  - name: test
    module: agent.tools.adapters.test:PytestTool
  - name: search
    module: agent.tools.adapters.search:GrepTool


Sample limits.yaml:

budgets:
  turn_seconds: 120
  turn_tokens: 200_000
  max_parallel_tools: 6
  max_plan_steps: 50
  max_tool_runtime_seconds: 90


Sample sandbox.yaml:

engine: gvisor        # or firejail or docker
network: disabled     # default outbound OFF
cpu_limit: "2"
memory_limit_mb: 4096
workdir: /workspace
mounts_readonly:
  - /usr/lib/python3.11
env_passthrough: []
seccomp_profile: src/agent/runner/seccomp/default.json


Sample retrieval.yaml:

embeddings:
  backend: sentence-transformers
  model: all-MiniLM-L6-v2
index:
  backend: faiss
  dim: 384
retriever:
  top_k_symbols: 24
  top_k_files: 12
  max_tokens_context_pack: 12000
  refresh_on_diff: true


Sample .env (excerpt):

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

4) Core contracts (types & signatures)

src/agent/orchestrator/types.py (sketch):

from typing import TypedDict, List, Dict, Any, Literal, Optional

class ToolCall(TypedDict):
    name: str
    id: str               # correlates request <-> result
    args: Dict[str, Any]

class ToolResult(TypedDict):
    id: str
    name: str
    ok: bool
    output: Any
    error: Optional[str]

class Step(TypedDict):
    id: str
    kind: Literal["read","search","edit","patch","run","test","explain"]
    deps: List[str]               # DAG edges
    parallelizable: bool
    tool: str                     # logical tool name
    args: Dict[str, Any]

class Plan(TypedDict):
    steps: List[Step]


DSPy Signatures

import dspy

class PlanSig(dspy.Signature):
    """Plan code changes and checks as a DAG.
    goal: str, repo_view: dict -> plan_json: str
    """

class RouteSig(dspy.Signature):
    """Map a step to a concrete tool invocation.
    step: dict -> tool_name: str, args_json: str, parallelizable: bool
    """

class CriticSig(dspy.Signature):
    """Score/critique a batch of results and suggest refinements.
    steps: list, results: list, repo_state: dict -> score: float, feedback: str
    """

5) Orchestrator flow (runtime)

src/agent/orchestrator/runtime.py (pseudocode):

async def run_turn(goal: str, repo_view: dict, state: TurnState) -> TurnState:
    plan = await Planner(goal=goal, repo_view=repo_view).plan_json  # JSON DAG
    steps = parse_plan(plan)
    for batch in topo_parallel_batches(steps):
        # Let the model emit native parallel tool calls if it can:
        maybe_calls = try_model_native_parallel(batch)
        if maybe_calls:
            results = await execute_tool_calls_parallel(maybe_calls)  # fan-out
        else:
            # Runtime-enforced parallelism:
            calls = [Router(step=s).to_call() for s in batch]
            results = await execute_tool_calls_parallel(calls)

        score, feedback = await Critic(steps=batch, results=results, repo_state=state.repo)
        state = state.with_results(batch, results, feedback)

        if need_refine(score):
            batch = refine_batch_with_feedback(batch, feedback)  # BestOfN/Refine

    return state


Parallelism: execute_tool_calls_parallel uses asyncio.gather by default; can flip to Ray for heavy jobs.

Idempotency: each ToolCall.id correlates results across retries.

Budgets: fail-fast on timeouts from limits.yaml.

6) Planner → DAG → Parallel Scheduler

Planner outputs a minimal DAG (read/search → edit/patch → run/test).

Scheduler groups ready steps with no unresolved deps and parallelizable=True, then executes them concurrently.

Critic receives the batch + outputs; it can gate progress or trigger refinement.

Termination: success when reward thresholds met (tests pass, lints clean, acceptance criteria satisfied).

7) Tooling: MCP-first + native adapters

MCP client (mcp_client.py) calls declared servers in config/mcp/clients.json.

Native adapters live in tools/adapters/* for tools not available via MCP or where ultra-low-latency is needed.

Policy gate wraps all tool calls (see §10).

Required logical tools (provide either MCP or native implementations):

fs.* – read/write files, list, mkdir (writes are policy-guarded)

git.* – status, diff, apply, commit, push (push is gated)

search.* – repo search/grep

run – run a single command in the sandbox

test – run tests, capture JUnit/coverage

fetch – HTTP GET (read-only by default)

docker.* – build/run (optional, gated)

8) Context Engine (“RepoGraph”)

Indexer builds an incremental code graph using Tree-sitter/LSP.

Embeddings created for symbols, docstrings, and comments.

Retriever assembles a compact context pack (top-K files/symbols/tests) within the token budget.

Diff-aware refresh: re-index changed files after each patch.

Required files:

context/indexer.py, repo_graph.py, retriever.py, embeddings.py

config/retrieval.yaml

data/ folders are created under runtime (see §13).

9) Model Router

Chooses provider/model per step (models/router.py) using models.yaml rules.

Surface a uniform tool-call transport shape for all providers.

Respect parallel_tool_calls when provider supports it; otherwise, fallback to runtime parallelism.

10) Execution & Safety

Sandbox (runner/sandbox.py): wraps gVisor/Firejail/Docker. Default outbound network = off.

OPA Policy (policy/gate.py, policy/opa_client.py): every tool call -> Rego decision.

Budgets from limits.yaml: per-turn time/token, per-tool runtime, max concurrent tools.

Example allow/deny (Rego) in policy/opa_policies/policy.rego:

package agent.tool

default allow = false

# Allow safe fs reads
allow {
  input.tool.name == "fs.read"
}

# Block outbound network by default
deny[msg] {
  input.tool.name == "run"
  input.args.network == "enabled"
  msg := "Outbound network disabled"
}

# Permit git push only for trusted users and no --force
allow {
  input.user.trust == "high"
  input.tool.name == "git.push"
  not input.args.force
}

11) Observability & Evals

Tracing: emit OpenTelemetry spans around every step/tool call.

Metrics: counters for step success/failure, p95 latencies, tokens, $$.

Evals: plug SWE-bench or your own tasks; reward functions live in evals/reward_functions.py.

12) CLI/TUI surface (developer workflow)

All commands stream logs and write artifacts under data/artifacts/<run_id>/.

# 1) Plan the work
agent /plan "Add pagination to /users and tests"

# 2) Inspect context
agent /ctx --files --symbols

# 3) Propose and review patch
agent /edit
agent /diff
agent /apply   # guarded write

# 4) Run & test in sandbox
agent /run "pytest -q"
agent /test

# 5) Commit & open PR
agent /commit -m "feat(users): pagination + tests"
agent /pr

13) Runtime data & required folders

The runtime creates/uses:

data/
├─ index/                 # vector + metadata
│  ├─ faiss.index
│  └─ meta.sqlite
├─ artifacts/             # per-run outputs (plans, tool I/O, diffs)
│  └─ <run_id>/
├─ logs/                  # text logs per run
└─ traces/                # otlp dumps (if not exported)


These folders must exist or be created at startup by scripts/bootstrap_repo.sh.

scripts/bootstrap_repo.sh should at least do:

#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/agent/{cli/orchestrator,context,tools/adapters,models/providers,runner/{seccomp,gvisor},policy/opa_policies,observability,evals,config/mcp}
mkdir -p data/{index,artifacts,logs,traces}
touch src/agent/__init__.py
touch src/agent/cli/__init__.py src/agent/orchestrator/__init__.py
touch src/agent/context/__init__.py src/agent/tools/__init__.py
touch src/agent/models/__init__.py src/agent/runner/__init__.py
touch src/agent/policy/__init__.py src/agent/observability/__init__.py
touch src/agent/evals/__init__.py src/agent/config/__init__.py
# Optional: seed config files if missing
[ -f src/agent/config/models.yaml ] || cat > src/agent/config/models.yaml <<'YAML'
# see AGENTS.md §3 for example content
YAML

14) Minimal code sketches (selected files)

src/agent/orchestrator/planner.py

import dspy, json

class PlanSig(dspy.Signature):
    """goal, repo_view -> plan_json"""

class Planner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.pred = dspy.ChainOfThought(PlanSig)  # compile with MIPRO/SIMBA

    def forward(self, goal: str, repo_view: dict) -> str:
        raw = self.pred(goal=goal, repo_view=repo_view).plan_json
        return raw

def plan(goal: str, repo_view: dict) -> dict:
    # validate/normalize plan JSON
    p = json.loads(Planner()(goal, repo_view))
    # ... ensure ids, deps, parallelizable flags, etc.
    return p


src/agent/orchestrator/router.py

import dspy, json
from .types import Step

class RouteSig(dspy.Signature):
    """step -> tool_name, args_json, parallelizable"""

class Router(dspy.Module):
    def __init__(self, policies):
        super().__init__()
        self.pred = dspy.Predict(RouteSig)
        self.policies = policies

    def forward(self, step: Step):
        out = self.pred(step=step)
        tool_name = out.tool_name
        args = json.loads(out.args_json or "{}")
        parallelizable = bool(out.parallelizable)
        # Safety: enforce deterministic rules
        self.policies.validate(tool_name, args)
        return tool_name, args, parallelizable


src/agent/orchestrator/scheduler.py

import asyncio
from .types import Plan, Step, ToolCall
from ..tools.dispatch import to_call
from ..policy.gate import allow_or_raise

def ready_batches(steps):
    # topo sort and group parallelizable steps with no pending deps
    # yield lists of steps (batches)
    ...

async def execute_tool_calls_parallel(calls: list[ToolCall]):
    tasks = [asyncio.create_task(invoke_call(c)) for c in calls]
    return await asyncio.gather(*tasks, return_exceptions=False)

async def invoke_call(call: ToolCall):
    allow_or_raise(call)                # OPA decision
    tool = resolve_tool(call.name)      # MCP or native adapter
    return await tool(call.args)


src/agent/tools/adapters/run.py

from ..schemas.tool_base import BaseTool
from ...runner.sandbox import Sandbox

class RunTool(BaseTool):
    name = "run"
    schema = {"command": "str", "timeout": "int?"}

    async def __call__(self, args):
        cmd = args["command"]
        timeout = args.get("timeout", 60)
        sb = Sandbox()
        return await sb.run(cmd, timeout=timeout)


src/agent/runner/sandbox.py

import asyncio, os

class Sandbox:
    def __init__(self, cfg=None):
        self.cfg = cfg or load_sandbox_cfg()

    async def run(self, command: str, timeout: int = 60):
        # Example: run in a gVisor or Firejail envelope
        wrapped = wrap_command(command, self.cfg)
        proc = await asyncio.create_subprocess_shell(
            wrapped,
            cwd=self.cfg.workdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=filtered_env(self.cfg),
        )
        try:
            outs, errs = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise
        return {"code": proc.returncode, "stdout": outs.decode(), "stderr": errs.decode()}


src/agent/policy/gate.py

from .opa_client import decide

def allow_or_raise(call):
    decision = decide({
        "tool": {"name": call["name"], "args": call["args"]},
        "user": current_user_context(),
    })
    if not decision.get("allow", False):
        msg = decision.get("deny_reason", "blocked by policy")
        raise PermissionError(msg)

15) Parallel tool calling (dual-path)

Model-native (provider supports it):

The assistant step returns a list of ToolCalls in one turn.

Runtime executes all calls concurrently, then returns a single message containing a list of ToolResults back to the model.

Preserves the “one-turn, many tools” rhythm (lower latency).

Runtime-enforced (provider doesn’t support parallel calls):

Planner marks steps parallelizable.

Router produces calls per step.

Scheduler fans them out with asyncio.gather (or Ray).

The model still sees a single “batch result” per planning chunk.

Both paths share the same ToolCall/ToolResult shapes, so the rest of the system doesn’t care which path executed them.

16) MCP configuration

src/agent/config/mcp/clients.json (example):

{
  "servers": [
    {"name": "fs",    "endpoint": "http://localhost:7331"},
    {"name": "git",   "endpoint": "http://localhost:7332"},
    {"name": "fetch", "endpoint": "http://localhost:7333"}
  ],
  "timeout_ms": 15000
}


src/agent/tools/mcp_client.py abstracts request/response to those servers.

17) Testing & quality gates

Unit tests for planner/router/scheduler.

Golden tests for context packs.

E2E tests using the examples/hello_world_repo (no real keys).

Reward functions (lints/tests/spec) drive Critic refinement loops.

18) Security notes (in practice)

Treat the runner as untrusted; keep default outbound network OFF.

Gate all writes and external side-effects via OPA.

Keep strict CPU/RAM/time budgets to prevent runaway jobs.

Never expose host filesystem; use ephemeral workspaces for runs.

19) How to start (MVP checklist)

 Create tree via scripts/bootstrap_repo.sh

 Fill models.yaml, tools.yaml, .env

 Implement minimal adapters: fs.read, search, run, test

 Implement Planner/Router/Scheduler skeletons

 Build RepoGraph indexer + embeddings; verify /ctx works

 Wire OPA gate (allow reads; deny risky ops by default)

 Add OTEL tracing and a basic dashboard

 Ship /plan, /diff, /run, /test in CLI

20) Appendix – Example CLI entrypoint

src/agent/cli/__main__.py

import typer
from rich import print
from agent.orchestrator.runtime of run_turn
from agent.context.retriever import build_repo_view

app = typer.Typer(add_completion=False)

@app.command("plan")
def plan(goal: str):
    repo_view = build_repo_view()
    state = run_sync(run_turn(goal, repo_view, state=new_state()))
    print("[bold green]Plan created.[/bold green]")

# ...similar: ctx, edit, diff, apply, run, test, commit, pr

if __name__ == "__main__":
    app()

21) License & attribution

This repository is intended to be open source (fill in your preferred license). The design relies on DSPy for program-level compilation and on the Model Context Protocol (MCP) for tool standardization, with native adapters where needed.

