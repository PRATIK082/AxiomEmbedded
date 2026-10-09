# AxiomEmbedded Audit — installability + standalone use

Date: 2026-10-09. Scope: README, AGENTS.md, PROJECT_SPEC.md, ROADMAP.md,
pyproject.toml, axiom_cli/, agents/, skills/, tools/, integrations/, clients/.
Method: direct file reads (no code executed). No code changed in this step.

## 1. What exists (verified by reading source)

- **Distribution entry points (declared, not verified end-to-end):**
  `pyproject.toml` (`name axiom-embedded`, `version 0.1.0`,
  `requires-python >=3.11`, `dependencies [PyYAML]`) already declares
  `[project.scripts] axiom = "axiom_cli.main:main"`, so `pipx install .`
  should create an `axiom` shim. `axiom_cli/__main__.py` re-exports `main`,
  so `python -m axiom_cli` works. Version is triple-duplicated:
  `pyproject.toml` / `VERSION` / `configs/project.yaml` (`product.version 0.1.0`).
  No `axiom --version` flag and no `version` subcommand exist.
- **CLI (`axiom_cli/main.py`, 194 lines, real code):** `doctor`,
  `repo validate` (+ `repo-validate` alias), `profile validate <path>`,
  `analyze <path>`, `graph build`, `context select`, `impact`,
  `workflow plan`, `route`, `engage`, `run`, `status`, `fix`, `feature`,
  `mcp` (delegates to `packages.axiom_mcp.server.serve`),
  `serve --port` (delegates to `packages.axiom_server.server.serve`).
  `run` only emits a plan-then-execute JSON plan; it does not execute anything.
  `doctor` checks python version + `validate_repo()` + a full `pytest -q` run;
  it does not check for OpenCode, node, pipx, providers, or versions.
- **Single-implementation SDK (`packages/axiom_sdk/__init__.py`):** `engage_skills`,
  `run_plan`, `read_skill`, `list_skills`, `list_profiles`; MCP/REST/A2A/CLI all
  delegate to it. Agreement is covered by `tests/test_interfaces.py`
  (asserts the automotive/mcu slice is 42 skills across SDK/CLI/MCP/REST/A2A).
- **Working MCP server (`packages/axiom_mcp/server.py`, 77 lines):**
  newline-delimited JSON-RPC 2.0 over stdio with 5 tools:
  `engage`, `run_plan`, `read_skill`, `list_skills`, `list_profiles`.
  Wired via `axiom mcp` and referenced by `clients/mcp.json`.
- **REST + A2A server (`packages/axiom_server/`):** `/v1/engage`, `/v1/run`,
  `/v1/a2a/tasks`, `/.well-known/agent.json` (agent card also checked into
  `integrations/a2a/agent-card.json`). Covered by the same interface test.
- **Agents as source content (28 dirs in `agents/`):** each sampled dir
  (`implementation/`) contains `AGENT.md` + `manifest.json` with id, version,
  capabilities, inputs/outputs, permissions, approval flags. Machine catalogs
  `registries/agents.json`, `registries/profiles.json` exist.
- **Skills as source content (47 dirs in `skills/`):** each sampled dir
  (`embedded-c/`) contains `SKILL.md` (frontmatter: name, description, version,
  domains, platforms) + `manifest.json` + `manifest.yaml`. Machine catalogs
  `registries/skills.json`, `registries/skill-index.json`,
  `registries/skill-facets.yaml` exist. Skill bodies are substantive
  (e.g. `embedded-c` cites ISO C17 / MISRA C:2025 / CERT C by reference + URL,
  no normative text vendored — compliant with the safety rule).
- **Tools layer (`tools/`, 10 dirs):** `change-impact`, `coverage-ingestor`,
  `dependency-analyzer`, `documentation-generator`, `report-generator`,
  `repository-analyzer`, `source-parser`, `static-analysis-aggregator`,
  `test-generator`, `traceability-checker` — directories exist (content audit
  per-tool not done; CLI `analyze`/`graph build` use `packages/context`, not
  `tools/` directly).
- **Client onboarding pointers (real, minimal):** root `AGENTS.md` (portable
  contract), `CLAUDE.md` + `GEMINI.md` (3-line pointers to `AGENTS.md`),
  `opencode.json` (instructions list + `permission` baseline with
  plan/reviewer agents), `clients/README.md` + `clients/COPILOT.md` +
  `clients/CURSOR.md` (wiring tables for MCP/CLI/REST/SDK), `clients/mcp.json`
  (stdio entry `python -m axiom_cli mcp`).
- **Contract/governance docs:** `PROJECT_SPEC.md` (artifact/relationship/profile/
  skill/agent/workflow/evidence definitions + non-goals), `AGENTS.md` working
  agreement + verification + git rules, `configs/project.yaml` (artifact-graph
  source of truth, approval gates for push/release/destructive/safety/security
  changes), `docs/client-matrix.md`, `examples/` (6 example projects incl.
  `brownfield-c-project`), `tests/` (6 files).
- **License:** `LICENSE` is Apache-2.0; `NOTICE` (1 line) covers standards-text
  non-redistribution + external migration. No OpenCode attribution yet.

## 2. What is only a document (claims without implementation)

- `integrations/mcp/server.py` is a 9-line `McpRegistry` stub (in-memory
  register, no stdio/transport); `integrations/mcp/server-manifest.json` lists 9
  aspirational tools (`repo.analyze`, `repo.index`, `graph.neighbors`,
  `context.select`, `profile.validate`, `workflow.plan`, `change.impact`,
  `evidence.record`, `audit.run`) that the real MCP server (`packages/axiom_mcp`)
  does **not** expose. The integrations README, `integrations/opencode/README.md`
  (3 lines), `integrations/copilot/README.md` (3 lines),
  `integrations/a2a/README.md` (3 lines) describe wiring that has no code behind it.
- `integrations/llm/provider.py` is a `Protocol` + `UnconfiguredProvider` that
  raises on use — no OpenAI/Anthropic/Gemini client, no streaming, retries, or
  token accounting.
- `REPOSITORY_INVENTORY.md` claims `.github/copilot-instructions.md`,
  `.github/instructions/`, `.github/prompts/`, `.github/agents/` exist; glob for
  `.github/**/*` returned nothing — either absent or not visible to the tool.
  Likewise `.opencode/**/*` glob returned nothing (no generated
  `.opencode/{agents,skills}` present). Treat both as missing until proven otherwise.
- ROADMAP 0.3–1.0 items (persistent index, C/C++ adapters, workflow state machine,
  schema-driven CLI/API, MCP skill packaging, A2A exchange, eval harness) and
  `docs/client-matrix.md` "agreement guarantee" beyond the 42-skill test are
  roadmap/spec text, not enforced behavior.
- Safety boundary: README §"Safety and certification boundary" text exists, but no
  mechanism appends it to generated reports or blocks compliance claims in output.

## 3. What is missing for install and standalone use

### Phase 1 — Distribution (all missing unless noted)
1. `pipx install .` + `axiom` entry: declared in pyproject but never tested here;
   no install test, no `--version`, doctor has no install-health checks.
   `clients/mcp.json` hardcodes `"cwd": "C:/D/Project/GitHub/AxiomEmbedded"`,
   which breaks on any other machine.
2. Top-level `axiom_mcp/` stdio server exposing **every** CLI command
   (`analyze`, `graph build`, `context select`, `impact`, `profile validate`,
   `research`) as typed tools with JSON schemas: missing — only
   `packages/axiom_mcp` with 5 tools and `params: [...]` name lists (no JSON
   Schema types/descriptions/required) exists.
3. `skills/` + `agents/` as single source of truth: content exists, but
   `scripts/sync_clients.py` does not exist (`scripts/` has `add_frontmatter.py`,
   `audit_skills.py`, `install_skills.py`, `migrate_oeelf.py`, `test_all.sh`,
   `verify_skill.py` only). None of the generated targets exist or are verified:
   `.opencode/{agents,skills}`, `opencode.json` (root file exists but is
   hand-maintained, no `mcp` section, no generator stamp), `.claude/{agents,skills}`,
   `.claude-plugin/plugin.json`, `.mcp.json`, `.github/copilot-instructions.md`,
   `GEMINI.md` (exists only as 3-line pointer, not generated). No CI check for
   generated-file freshness.
4. `axiom install --client <opencode|claude|codex|gemini|copilot> [--global]`:
   no such subcommand; no per-client installer; no temp-project test per client.

### Phase 2 — Standalone runtime (original spec) / OpenCode launcher (amendment)
- Original-spec items are entirely absent: no `axiom_runtime/` (LLM client, agent
  loop, built-in read/write/edit/glob/grep/shell/git tools, permission model, audit
  log, sessions/compaction, REPL/slash commands, headless `--json` execution),
  no `axiom.toml` config, no subagent runner. Per the amendment these are
  **intentionally not to be built** (custom runtime deferred).
- Amendment Phase 2 items are all missing: no `docs/OPENCODE_COMPAT.md` (no
  recorded OpenCode version/schema/permissions/commands/headless findings), no
  OpenCode license attribution in `NOTICE`, no `axiom`/`axiom tui`/`axiom run`/
  `axiom research` launcher with isolated config dir, no `axiom doctor` OpenCode
  detection/pinned-install, no `--provider`/`--model` passthrough or local-model
  support, no `/axiom-*` OpenCode commands, no OpenCode-native subagents
  (requirement/architecture/code/test/review/debug with allowlists), no TypeScript
  hooks plugins (evidence writer, protected-path guard, redacted tool-call log),
  no headless integration test against `examples/brownfield-c-project` in CI.

### Phase 3 — Deep research (missing under both specs)
- No `axiom_research/` or `axiom research` command, no research MCP tool or skill,
  no planner→searchers→fetch→verifier→synthesizer pipeline, no search backends
  (SearXNG/Brave/Tavily/no-key fallback), no citation/confidence/evidence-graph
  writer, no standards-paraphrase-only guard, no safety-notice injection.
- The closing deep-research task (OpenCode vs Claude Code vs Codex CLI vs Gemini
  CLI feature comparison with official-docs-only citations) has no tooling behind
  it; it must be done manually with web sources.

### Phase 4 — Docs and release (missing)
- README quick start still documents `python -m axiom_cli ...` only (no
  `pipx install axiom-embedded` → `axiom doctor` → `axiom` flow, no per-client
  install, no launcher→OpenCode→MCP→artifact-graph diagram, no Compatibility
  table). CHANGELOG (single `0.1.0` line), ROADMAP (no "custom runtime deferred"
  note), PROJECT_SPEC, VERSION bump, PyPI publish, and release tag are all pending.

## 4. Audit verdict / recommended order
1. Phase 1a: verify `pipx install .`, add `--version`, fix/portabilize
   `clients/mcp.json`, harden `doctor`. 2. Phase 1b: build `axiom_mcp/` with full
   tool coverage + JSON schemas. 3. Phase 1c: `scripts/sync_clients.py` + all
   generated targets + CI freshness check. 4. Phase 1d: `axiom install --client`
   + temp-project tests. Then amended Phase 2 (compat doc first), Phase 3
   (research), Phase 4 (docs/release). No code was changed in this audit.
