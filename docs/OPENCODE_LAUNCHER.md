# Axiom OpenCode launcher (`axiom oc`)

Axiom is a domain layer, not a runtime: `axiom oc` shells out to a
user-installed `opencode` binary with an Axiom-owned isolated config.
Compatibility scope and the version gate live in
[OPENCODE_COMPAT.md](OPENCODE_COMPAT.md).

## Verbs

| Command | Effect |
|---|---|
| `axiom oc tui [--dir D] [--model M] [--agent A]` | Interactive TUI session |
| `axiom oc run <message> [--dir D] [--model M] [--agent A] [--format json] [--title T]` | Headless `opencode run` session |
| `axiom oc research <question> [--model M] [--dir D]` | Headless run framed research-only, via the `explore` agent (no file changes) |

Every verb accepts `--source DIR` (axiom content source; default:
auto-detect), `--no-isolate` (use the operator's own OpenCode config),
and `--dry-run` (print resolved argv/env/config, execute nothing).

## Isolation model

By default the launcher sets, for the child process only:

- `OPENCODE_CONFIG` → `~/.axiom/opencode/opencode.json` (Axiom-generated:
  optional `model` passthrough plus the `axiom` MCP entry). Only files
  under `~/.axiom/` are ever written; user config is never touched.
- `OPENCODE_CONFIG_DIR` → the content source's `.opencode/` (agents,
  `/axiom-*` commands, policy plugin) when a source checkout is
  available; otherwise config-file isolation only, stated honestly.

## Providers, models, credentials

Axiom keeps no model catalog — `--model provider/id` passes straight
through to `opencode run`, and credentials stay in the operator's
environment (e.g. `ANTHROPIC_API_KEY`), inherited by the child process.
Local models work the same way: configure an OpenAI-compatible endpoint
in your own opencode config (see the OpenCode providers documentation),
then launch with `--no-isolate --model <local-model-id>`.

## Policy plugin

`.opencode/plugins/axiom-policy.ts` (shipped by `axiom install
--client opencode`) does three narrow things: it refuses reads of
secrets files (`.env*`), it appends the Axiom working contract across
session compaction, and — only when `AXIOM_TOOL_LOG` points at a path —
it appends redacted `{tool, session}` JSONL lines (never arguments or
output). Behavior is covered by `tests/test_headless.py` and the
`opencode-headless` CI workflow, which run keyless: config validation,
MCP handshake, and the dry-run contract against the real binary.
Keyed live-model runs remain a manual release-gate check.
