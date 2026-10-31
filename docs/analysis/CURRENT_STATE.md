# AxiomEmbedded Current State (2026-10-11, v0.2.0)

## Purpose
Open AI-native engineering platform for embedded & cyber-physical systems. Artifact graph is source of truth; V-model + brownfield workflows; domain-neutral core with composable domain overlays.

## Architecture
- `axiom_cli/main.py`: CLI (analyze, graph build, context select, impact, workflow plan, route, engage, packs, compose, run, status, fix, feature, research, install, oc, mcp, stage, serve).
- `axiom_mcp/server.py`: 21 typed stdio tools mirroring CLI via `packages/axiom_sdk` (single implementation).
- `packages/`: context (indexer/selector), workflow (entry/stage/engine), agents (router), skills (engage), toolpacks, compose, research, installer, axiom_ops, launcher.
- `skills/<id>/SKILL.md` + `manifest.yaml` (facets: domains/platforms, v1.2.0/1.3.0). Flat IDs (e.g. `autosar`, `automotive-diagnostics`). 58 skills registered.
- `registries/skill-index.json` (skills + by_domain/by_platform) is the discovery index; `registries/skills.json` is id->path catalog.
- `profiles/*.yaml`, `domains/`, `platforms/`, `standards/` (metadata only, no normative text), `rules/`, `workflows/`, `schemas/`, `tools/` (e.g. `tools/diag-uds-testgen/` deterministic generator).
- `scripts/sync_clients.py` generates 155 client files; CI freshness gate.

## Entry points
CLI `axiom`, MCP stdio `axiom mcp`, SDK `packages/axiom_sdk`, REST `axiom serve`.

## Tests/CI
`tests/test_*.py` (contracts, skills packaging, compose, toolpacks, research, install, launcher). `test_skills_packaging.py` enforces frontmatter {name,description,version,domains,platforms}, manifest facets, index linkage. PyYAML only, py>=3.11.

## Gaps (summary)
No rich catalog.yaml/registry.yaml with maturity/inputs/outputs/deps; no loader/validator/runner with run manifests + dry-run; no create/validate/run/report skill commands; no per-skill checklists/templates/scripts/tests convention; no skill CI; no traceability run-manifests under .axiom/runs/.
