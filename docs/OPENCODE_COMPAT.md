# OpenCode compatibility record

Status: **surveyed 2026-10-09, no code written**. This document is the
Phase 2 step-0 gate required by the project amendment: verify OpenCode
docs and changelog *before* building the `axiom` launcher on top of
OpenCode. All generated client files remain **provisional** until the
launcher work in this phase confirms them against a pinned OpenCode.

## Tested version

- Local OpenCode: **1.18.31** (`opencode --version`, Chocolatey install).
- Latest upstream v1 at survey time: **1.18.35** (2026-10-06).
- Docs tree surveyed: `https://opencode.ai/docs` (last updated 2026-10-08).

## Pinning decision

- **Phase 2 targets the v1 line only.** Pin minimum `>=1.18.31`
  (the locally tested version); recommend latest v1 patch.
- **v2 is out of scope for Phase 2.** Upstream ships a separate major
  line (v2.0.6 at survey time, npm `@opencode/cli`, separate
  `/v2/docs` tree, `opencode pair` instead of `opencode web`-style
  flows). The v1 and v2 config/command surfaces must be assumed
  divergent until someone surveys `/v2/docs` the way this document
  surveys v1. Record v2 support as future work in ROADMAP, not as
  a Phase 2 deliverable.
- Changelog v1.18.31 → v1.18.35 contains **bugfixes only** (provider
  SDK bumps, macOS signing, timeout defaults, Copilot/ACPs fixes).
  No config-schema, CLI-flag, agent-frontmatter, command-frontmatter,
  plugin-hook, or MCP-config breaking changes were found in that
  range. Re-check the changelog before release; the launcher must
  fail closed (see doctor rule below) on untested majors.

## License and attribution

- OpenCode is **MIT licensed** (`Copyright (c) 2025 opencode`,
  verified from the upstream LICENSE file at survey time).
- Attribution is recorded in `NOTICE` at the repository root.
- Axiom does not vendor OpenCode. The launcher shells out to a
  user-installed `opencode` binary.

## Integration surface (v1, verified against docs)

### Headless execution — the launcher primitive

- `opencode run [message..]` is the supported non-interactive entry
  point for scripting and automation.
- Flags the launcher will rely on: `--model/-m provider/model`,
  `--agent`, `--dir`, `--format (default|json)`, `--continue/-c`,
  `--session/-s`, `--title`, `--file/-f`, `--command`,
  `--attach <url>`, `--auto` (auto-approve only permissions that are
  not explicitly denied).
- `opencode serve` + `opencode run --attach <url>` avoids MCP cold-boot
  cost per invocation; the launcher may use this for repeated calls.
- TUI launch is plain `opencode [project]` with `--model`, `--agent`,
  `--prompt`, `--auto` flags.

### Isolated config — the key launcher mechanism

- `OPENCODE_CONFIG` (custom config file path) and
  `OPENCODE_CONFIG_DIR` (custom directory searched for
  `agents/ commands/ modes/ plugins/` like `.opencode/`) give the
  launcher full config isolation: Axiom can point OpenCode at
  Axiom-owned config without touching the user's own setup.
- `OPENCODE_CONFIG_CONTENT` (inline JSON) allows runtime overrides.
- Config sources merge (not replace) in precedence order:
  remote → global → `OPENCODE_CONFIG` → project → `.opencode` dirs →
  inline → managed. The launcher must assume the user's global/project
  config still merges in; Axiom-owned agents/commands ship via
  `OPENCODE_CONFIG_DIR`, and Axiom defaults that must win go inline
  via `OPENCODE_CONFIG_CONTENT`.
- `opencode debug config` prints the resolved config and is the
  launcher/doctor verification primitive.
- Auth material lives outside our config (`~/.local/share/opencode/auth.json`
  via `/connect`); the launcher never writes credentials.

### Providers and models — passthrough, no Axiom registry

- Model selection is always `provider/model` (`--model`,
  `model`/`small_model` config keys, per-agent and per-command
  `model` overrides).
- 75+ providers via AI SDK / Models.dev; `opencode models [provider]`
  lists, `--refresh` updates the cache.
- Local models are plain custom providers with
  `npm: @ai-sdk/openai-compatible` + `options.baseURL`
  (documented patterns: Ollama `http://localhost:11434/v1`,
  LM Studio `http://127.0.0.1:1234/v1`,
  llama.cpp `http://127.0.0.1:8080/v1`, Atomic Chat).
  The launcher passes provider/model through verbatim and documents
  the local-model recipe; it does not maintain a model catalog.
- `provider.<id>.options`: `baseURL`, `apiKey` (`{env:...}` /
  `{file:...}` substitution supported in config), timeouts
  (`timeout`, `headerTimeout`, `chunkTimeout`, `false` disables),
  `blacklist`/`whitelist` model filters.
  `disabled_providers` beats `enabled_providers`.
- Credentials env-var passthrough (e.g. `AWS_PROFILE`,
  `AZURE_RESOURCE_NAME`) works because the launcher execs OpenCode
  in-process-environment.

### Agents — OpenCode-native subagents with allowlists

- Markdown agents in `.opencode/agents/` (or
  `~/.config/opencode/agents/`, or `OPENCODE_CONFIG_DIR/agents/`);
  filename becomes agent name; frontmatter `description` is required.
- `mode: primary | subagent | all` (default `all`); built-ins: primary
  `build` (default, full tools) and `plan` (edits/bash ask);
  subagents `general` (full tools), `explore` (read-only),
  `scout` (external-docs research).
- Permissions are the tool allowlist mechanism: per-agent
  `permission:` with `allow | ask | deny` per key
  (`read edit glob grep list bash task external_directory todowrite
  webfetch websearch lsp skill question doom_loop`),
  glob patterns for MCP tools (`"mymcp_*": "deny"`),
  per-bash-command globs (`bash: {"git *": ask}` with `*` first,
  last match wins), and `permission.task` globs controlling which
  subagents an agent may invoke (denied subagents disappear from the
  Task tool description).
- Legacy agent `tools:` map is **deprecated** in favor of
  `permission:` — Axiom generates `permission:` only.
- `subagent_depth` (default 1), `steps`, `temperature`, `hidden`
  (subagents only), `default_agent` (must be primary) complete the
  surface the launcher needs.

### Slash commands — `/axiom-*` mapping confirmed

- Markdown commands in `.opencode/commands/` (also global and
  `OPENCODE_CONFIG_DIR` locations); filename becomes `/name`;
  frontmatter `description`, optional `agent`, `model`, `subtask`;
  body is the template with `$ARGUMENTS` / `$1..$N`, `` !`cmd` ``
  shell injection, `@file` references.
- `subtask: true` forces subagent invocation without polluting primary
  context — the mapping for research-style `/axiom-*` commands.
- Custom commands can override built-ins; Axiom uses the `axiom-`
  prefix and must never shadow built-ins.

### Hooks — TypeScript plugins

- Local plugins: `.opencode/plugins/*.js|ts` (also global and
  `OPENCODE_CONFIG_DIR`), auto-loaded at startup; npm plugins via
  `plugin: [...]` config, installed with Bun into
  `~/.cache/opencode/node_modules/`.
- Plugin functions receive `{project, client, $, directory, worktree}`
  and return hook maps; typed via `@opencode-ai/plugin`
  (`import type { Plugin } from "@opencode-ai/plugin"`).
- Relevant hook events for Axiom: `tool.execute.before/after`
  (policy gates, e.g. deny `.env` reads), `permission.asked/replied`,
  `session.created/compacted/error/idle`, `command.executed`,
  `file.edited`, `experimental.session.compacting` (domain context
  that survives compaction — directly useful for Axiom traceability).
- The repo already carries `@opencode-ai/plugin` 1.18.31 in
  `.opencode/` (found in Phase 0 audit), matching the pinned v1 line.

### MCP — axiom_mcp wiring confirmed

- Local MCP: `mcp.<name> = {type: "local", command: [...], cwd,
  environment, enabled, timeout}`; remote: `{type: "remote", url,
  headers, oauth, enabled, timeout}`; `{env:...}` substitution works.
- Per-agent scoping: disable globally (`tools: {"axiom_*": false}`),
  enable per agent (`agent.<name>.tools` / permission globs).
  MCP tools are namespaced `<server>_*`.
- Phase 1 `axiom_mcp` (stdio, 20 tools) plugs in as one `local`
  entry: `command: ["axiom", "mcp"]` (or `python -m` fallback —
  same rule as the Phase 1 installer).
- `opencode mcp list/add/auth/debug` manage servers at runtime.
- Verified keyless against 1.18.31 (Phase 2c): config validation
  rejects the generic `{command, args}` split — OpenCode requires
  strict `{type: "local", command: [...], enabled: ...}` (fixed in
  sync/installer/launcher); the `initialize` result must carry
  `{protocolVersion, capabilities, serverInfo}` (fixed in
  `axiom_mcp`). Both entries report `connected` with no API key.

## Doctor rule (binding on launcher work)

`axiom doctor` must detect the `opencode` binary, parse
`opencode --version`, and:

- pass on v1 within the tested range,
- warn (not fail) on newer v1 patches with a "re-verify" pointer to
  this document,
- **fail closed** on v2+ (or unparseable versions) until v2 is
  surveyed, with an explicit override flag for operators who accept
  the risk.

## Re-verification cadence

- Before any Axiom release: re-run `opencode --version` against
  latest v1, scan the changelog for config/CLI/agent/command/plugin/MCP
  breaking changes, and bump the "tested version" line above.
- On any OpenCode major (v2+): full re-survey, new compat section,
  no silent carry-over of v1 assumptions.
