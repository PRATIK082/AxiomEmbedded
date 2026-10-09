# AxiomEmbedded roadmap

## Phase 3 Deep research (done)
- Planner → searchers → verifier → synthesizer (`packages/research.py`) — done.
- `axiom research` + `research` MCP tool with `auto|opencode|local` (+ key-gated
  web stubs) backends — done.
- Remaining: live web search wiring once credentials exist; the closing
  OpenCode-vs-Claude-Code-vs-Codex-vs-Gemini comparison stays a manual
  official-docs-only task until then.

## Phase 2 OpenCode runtime layer (done)
- OpenCode docs/changelog survey → `docs/OPENCODE_COMPAT.md` + `NOTICE` attribution — done.
- `axiom oc tui|run|research` isolated-config launcher + doctor pin — done.
- `/axiom-*` slash commands + `axiom-policy` hooks plugin + OpenCode-native subagents — done.
- Provider/model passthrough + local-model recipes + headless CI — done.
- Remaining: re-survey when moving off the tested v1 range; custom runtime stays
  deferred unless OpenCode proves insufficient.

## Phase 1 Distribution (done)

- Installable wheel (`pipx install .`, `axiom` entry point) — done.
- `axiom_mcp/` stdio server with typed tools for every CLI command — done.
- `skills/`/`agents/` as single source of truth + generated client files + CI check — done.
- `axiom install --client` for opencode/claude/codex/gemini/copilot — done.
- Remaining: PyPI publish, VERSION bump, release tag (Phase 4).

## 0.1 Foundation (current)

- Normalize AxiomEmbedded  into the AxiomEmbedded product model.
- Keep AxiomEmbedded  migration support external; do not vendor legacy snapshots into the active tree.
- Define artifact graph, context engine, evidence ledger and agent contracts.
- Add AI-client onboarding files for Copilot/OpenCode/compatible agents.
- Establish domain/platform/profile composition.

## 0.3 Functional platform

- Persistent repository index and change graph.
- C/C++ symbol/dependency extraction adapters.
- Real workflow state machine and evidence store.
- Schema-driven CLI/API.
- MCP server implementation behind a stable tool/resource registry.

## 0.4 Engineering automation

- Unit/integration/test generation adapters.
- Static-analysis aggregation.
- Coverage ingestion.
- Requirement/code/test traceability automation.
- Brownfield architecture recovery.

## 0.5 Agent platform

- Agent registry and permission model.
- Specialist agent handoffs.
- MCP skill/resource packaging.
- A2A agent cards and task exchange.
- Agent evaluation and regression harness.

## 0.6 Domain expansion

Automotive → Embedded Linux → Industrial → Robotics → Aerospace/Space → Defense → broader cyber-physical domains.

## 1.0

Stable artifact model, plugin API, workflow contracts, evidence format and agent interoperability contracts suitable for an open-source ecosystem.
