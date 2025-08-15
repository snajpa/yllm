#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/agent/{cli/commands,orchestrator,context,tools/adapters,models/providers,runner/{seccomp,gvisor},policy/opa_policies,observability,evals,config/mcp}
mkdir -p data/{index,artifacts,logs,traces}
# Create __init__ files for packages
for pkg in src/agent src/agent/cli src/agent/cli/commands src/agent/orchestrator src/agent/context src/agent/tools src/agent/tools/adapters src/agent/models src/agent/models/providers src/agent/runner src/agent/policy src/agent/observability src/agent/evals src/agent/config; do
  touch "$pkg/__init__.py"
done
# Seed config files if missing
[ -f src/agent/config/models.yaml ] || echo "# model routing config" > src/agent/config/models.yaml
[ -f src/agent/config/tools.yaml ] || echo "# tools config" > src/agent/config/tools.yaml
[ -f src/agent/config/limits.yaml ] || echo "# limits config" > src/agent/config/limits.yaml
[ -f src/agent/config/sandbox.yaml ] || echo "# sandbox config" > src/agent/config/sandbox.yaml
[ -f src/agent/config/retrieval.yaml ] || echo "# retrieval config" > src/agent/config/retrieval.yaml
[ -f src/agent/config/mcp/clients.json ] || echo '{"servers":[]}' > src/agent/config/mcp/clients.json
