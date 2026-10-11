# Changelog

## Unreleased — Axiom Skill Framework (2026-10-11)

Additive skill framework + 30 original `axiom-*` workflow skills:

- `skills/catalog.yaml` (88 skills) + `skills/registry.yaml`; dual
  frontmatter contract (legacy keys + `axiom:` block) keeps all packaging tests green.
- Framework core: `packages/skills/{registry,loader,validator,runner}.py`;
  CLI `axiom skills list|validate|search|run|report|create` (dry-run default);
  MCP `search_skills|validate_skill|run_skill|create_skill` (21 → 25 tools).
- Two beta exemplars with checker scripts + tests:
  `axiom-autosar-classic-bsw-integration`, `axiom-diagnostics-uds`;
  28 experimental scaffolds with workflows, checklists, templates.
- `scripts/{validate_skills,create_skill,scaffold_axiom_skills,extend_catalog,sync_skill_index}.py`;
  `tests/test_skill_framework.py`; `.github/workflows/skill-validation.yml`.
- Docs: `docs/SKILL_FRAMEWORK.md`, `docs/skills/{AUTHORING_GUIDE,CONTRIBUTING,CATALOG}.md`,
  `docs/{skill-authoring-guide,mcp-tool-development-guide,skill-quality-gates,skill-gap-analysis,mcp-tool-backlog,current-state-assessment}.md`,
  `docs/analysis/{CURRENT_STATE,GAP_ANALYSIS,INTEGRATION_PLAN,FINAL_IMPLEMENTATION_REPORT}.md`,
  `docs/migration/EXISTING_CAPABILITY_MAPPING.md`; README “Axiom Skill Framework”.
- No existing capability removed/renamed; no reference-repo text used.
- Linking pass: `skills/links.yaml` + `link_related_skills.py` wire legacy
  bases to axiom-* specializations (extends/related/sub_skills, siblings,
  domain overlays) — no duplicates; future links via `--set`.
- Derived `manifest.json` export (`axiom skills manifest`, MCP
  `skill_manifest`; 26 tools): SKILL.md stays single source of truth.
- P1 generator wrappers (`packages/skill_tools.py`, SDK + MCP, 26 → 33
  tools): `analyze_repository`, `generate_checklist`, `generate_test_plan`,
  `generate_traceability_matrix`, `generate_report`, `review_configuration`,
  `analyze_trace` — deterministic, read-only except repo-confined
  `output_path` writes (dry-run default); skill-id allowlist, no `..`
  escape, secret scan reports line numbers only. Tests:
  `tests/test_skill_tools.py` (19 tests).


## 0.2.0 (2026-10-09)

Distribution (pipx/`axiom` entry, typed MCP server, single-source client
generation, per-client installer), OpenCode runtime layer (surveyed compat,
isolated-config launcher, slash commands, policy plugin, native subagents,
headless CI), and deep research (`axiom research` + MCP tool with
OpenCode-subagent primary and keyless local fallback backends).

### Deep research (Phase 3)
- New `packages/research.py` pipeline: planner → searchers → verifier →
  synthesizer with citations, confidence, paraphrase-only standards guard,
  and an injected safety notice on every report.
- `axiom research "q" [--backend auto|opencode|local|tavily|brave|searxng]
  [--max-subquestions N] [--format json|markdown] [--output FILE] [--model M]`;
  `auto` runs OpenCode `skill-researcher` subagents, falling back per question
  to the keyless local backend (ranked `skills/*/` manifest search, always
  available). Web backends are key-gated and honestly unavailable without
  credentials. The `research` MCP tool serves the same pipeline.

## OpenCode runtime layer (Phase 2)
- `docs/OPENCODE_COMPAT.md`: OpenCode docs/changelog survey (tested v1.18.31–1.18.35;
  v2 out of scope) + MIT attribution in `NOTICE`.
- New `axiom oc tui|run|research` launcher (isolated config under
  `~/.axiom/opencode`, `--model/--agent/--dir/--format` passthrough, `--dry-run`);
  `axiom doctor` now detects/pins the OpenCode binary.
- `scripts/sync_clients.py` generates 8 `/axiom-*` slash commands, the
  `axiom-policy` hooks plugin (blocks `.env` reads), and OpenCode-native
  `mode: subagent` frontmatter with permission allowlists; `axiom install`
  ships commands + plugin for opencode.
- MCP interop fixes verified against keyless `opencode mcp list`: OpenCode-shaped
  `{type: "local", command: [argv...]}` entries, `initialize` echoes the
  client's `protocolVersion` (+ `notifications/initialized` handler).
- Headless CI (`.github/workflows/opencode-headless.yml`) + `docs/OPENCODE_LAUNCHER.md`
  (verbs, isolation, model passthrough incl. local-model recipes, plugin).

## Distribution (Phase 1)
- `axiom --version` / `axiom version`; hardened `axiom doctor` (`--skip-tests`,
  installed-distribution aware, fixed wheel build via explicit package list).
- New `axiom_mcp/` stdio server: 19 typed tools with JSON schemas covering every
  CLI command; `axiom mcp` now serves it.
- `skills/` + `agents/` are the single source of truth: `scripts/sync_clients.py`
  generates 155 client files (`.opencode/`, `.claude/`, `opencode.json`,
  `.claude-plugin/plugin.json`, `.mcp.json`, `.github/copilot-instructions.md`,
  `GEMINI.md`) with a CI freshness gate.
- New `axiom install --client <opencode|claude|codex|gemini|copilot> [--global]`
  (merge-only, idempotent, tested per client in temp projects).
- `axiom research` surface reserved in Phase 1; implemented in Phase 3 below
  (deep-research pipeline).

## 0.1.0
- Initial starter.