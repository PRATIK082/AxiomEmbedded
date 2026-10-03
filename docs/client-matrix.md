# Client × Interface matrix

How each of the 11 supported clients reaches the 5 platform interfaces.
The platform does not care which client calls — behavior is identical because
every interface is backed by `packages/axiom_sdk`.

| # | Client | MCP | A2A | REST | CLI | Python SDK | Notes |
|---|--------|-----|-----|------|-----|------------|-------|
| 1 | GitHub Copilot | ✅ `.vscode/mcp.json` | — | ➖ via extension host | ✅ scripts | ✅ in-repo | `clients/COPILOT.md` |
| 2 | OpenCode | ✅ `opencode.json` mcp | — | ➖ | ✅ shell tool | ✅ | Tools auto-appear |
| 3 | Claude-based agent | ✅ `claude mcp add` | ✅ task peer | ✅ | ✅ | ✅ | Full coverage |
| 4 | GPT-based agent | ✅ config / Codex | ✅ task peer | ✅ | ✅ | ✅ | REST simplest for API agents |
| 5 | Gemini-based agent | ✅ config | ✅ task peer | ✅ | ✅ | ✅ | REST fallback documented |
| 6 | Cursor-style IDE | ✅ settings | — | ➖ | ✅ terminal | ✅ | `clients/CURSOR.md` |
| 7 | VS Code | ✅ `mcp.json` | — | ➖ | ✅ terminal | ✅ | Same as Copilot row |
| 8 | Custom AI | ✅ stdio spawn | ✅ agent card | ✅ | ✅ | ✅ | A2A discovery via `/.well-known/agent.json` |
| 9 | Local LLM | ➖ adapter needed | ➖ | ✅ recommended | ✅ recommended | ✅ | Serve once, call `/v1/run` |
| 10 | Web application | — | ✅ | ✅ recommended | — | ✅ backend | `/v1/skills|engage|run` |
| 11 | CLI / scripts | — | — | ✅ localhost | ✅ recommended | ✅ | `axiom engage|run|serve` |

Legend: ✅ first-class · ➖ possible via adapter · — not applicable.

## Interface reference

- **MCP (stdio):** `python -m axiom_cli mcp` — tools `engage`, `run_plan`,
  `read_skill`, `list_skills`, `list_profiles`. Config: `clients/mcp.json`.
- **A2A:** `GET /.well-known/agent.json` (card), `POST /v1/a2a/tasks`
  (`{message|request, domain?, platform?}` → `{taskId, status, artifact}`).
- **REST:** `GET /v1/skills`, `GET /v1/skills/{id}`, `POST /v1/engage`,
  `POST /v1/run`, `GET /v1/profiles`. Serve: `python -m axiom_cli serve [--port 8765]`.
- **CLI:** `engage --domain --platform`, `run <request> [--domain] [--platform]`,
  `mcp`, `serve`, plus existing `doctor|repo|profile|graph|context|impact|workflow|route`.
- **Python SDK:** `from packages.axiom_sdk import engage, run_plan, read_skill,
  list_skills, list_profiles`. Zero new dependencies.

Approval gates (`approval_required_for`) are returned by every planning path
on every interface; enforcement lives in the host workflow (`workflows/…`,
`configs/project.yaml`), never in client-specific code.
