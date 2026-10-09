# Changelog

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