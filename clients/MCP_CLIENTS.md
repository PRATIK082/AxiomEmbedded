# AxiomEmbedded — MCP client matrix (10 clients)

`axiom install --client <name>` wires all of these automatically
(`--global` for user scope, `--domains d1,d2` / `--groups g1,g2` for scoped
skill copies, `axiom uninstall` removes, `axiom update` refreshes).
This file documents what the installer does per client and the manual
fallback for the two hand-managed configs (Aider, Kilo Code).

Server command (auto-detected; `axiom mcp` shim preferred):

```json
{"command": "axiom", "args": ["mcp"]}
```

Fallback: `{"command": "python", "args": ["-m", "axiom_cli", "mcp"]}`.

| Client | Project scope | Global scope | Skills copied? |
|---|---|---|---|
| opencode | `opencode.json` + `.opencode/` | `~/.config/opencode/` | yes (agents/skills/commands/plugins) |
| claude (Claude Code) | `.mcp.json` + `.claude/` | `~/.claude.json` + `~/.claude/` | yes (agents/skills) |
| codex | `.codex/config.toml` | `~/.codex/config.toml` | no (reads AGENTS.md) |
| gemini (Gemini CLI) | `.gemini/settings.json` + `GEMINI.md` | `~/.gemini/` | instruction file only |
| copilot (VS Code / Coding Agent / Agent Mode) | `.github/copilot-instructions.md` (+`.vscode/mcp.json`, see `clients/COPILOT.md`) | n/a (per-repo) | instruction file only |
| cursor | `.cursor/mcp.json` | `~/.cursor/mcp.json` | no (runtime via MCP) |
| cline | `.cline/mcp.json` | `~/.cline/mcp.json` | no (runtime via MCP) |
| aider | `.aider.conf.yml` | `~/.aider.conf.yml` | no (runtime via MCP) |
| kilo (Kilo Code) | `.kilo/kilo.jsonc` | `~/.config/kilo/kilo.jsonc` | no (runtime via MCP) |
| openhands | always `~/.openhands/mcp.json` | same file | no (runtime via MCP) |

Clients that copy no skill files still get full skill access: `search_skills`,
`engage`, `read_skill`, and `run_skill` run server-side over MCP.

## Manual fallback — Aider

If `.aider.conf.yml` already exists the installer keeps it untouched. Add:

```yaml
mcp-servers:
  axiom-embedded:
    command: axiom
    args: [mcp]
```

## Manual fallback — Kilo Code

If the `kilo.jsonc` already exists the installer keeps it untouched (JSONC
comments are not machine-mergeable). Add under the `mcp` key:

```json
"axiom-embedded": {"command": "axiom", "args": ["mcp"]}
```

## Uninstall / update

- `axiom uninstall --client <name>`: unmerges the MCP entry, deletes copied
  files only on byte-match (divergent = user-owned = kept + reported).
- `axiom update --client <name>`: re-installs, then lists `stale` files
  (kept by default; refresh explicitly per file).
