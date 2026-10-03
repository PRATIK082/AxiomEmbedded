# Repository inventory

## Active product layers

- `apps/` user-facing applications and API entry points
- `packages/` reusable core/runtime libraries
- `agents/` specialist agent contracts
- `skills/` reusable engineering/platform/domain/AI capabilities
- `domains/` domain overlays
- `platforms/` compute/OS/platform overlays
- `profiles/` project compositions
- `rules/` machine-readable project controls
- `standards/` metadata/applicability references, not normative text
- `workflows/` lifecycle/change workflows
- `artifacts/` project artifact conventions
- `schemas/` stable machine-readable contracts
- `integrations/` MCP/A2A/LLM/IDE/Git adapters
- `tools/` repository/source/test/document analysis tools
- `hardware/` hardware/system modelling
- `simulation/` SIL/MIL/HIL/virtual platforms
- `evaluation/` AI and engineering regression suites
- `tests/` platform tests
- AxiomEmbedded  migration is external; no legacy snapshot is vendored

## Agent onboarding files

- `AGENTS.md` — portable repository contract
- `CLAUDE.md` — lightweight compatibility pointer
- `GEMINI.md` — lightweight compatibility pointer
- `.github/copilot-instructions.md` — GitHub Copilot repository-wide instructions
- `.github/instructions/` — path-specific Copilot instructions
- `.github/prompts/` — reusable Copilot prompts
- `.github/agents/` — Copilot custom-agent definitions
- `opencode.json` — OpenCode instruction/permission baseline

## Repository policy

- No vendored AxiomEmbedded /legacy snapshot is part of the active product tree.
- Brownfield and legacy-product capabilities remain supported through the active `skills/`, `agents/`, `workflows/` and `examples/` layers.
- AxiomEmbedded  migration accepts an external source directory through `scripts/migrate_AxiomEmbedded .py`.
