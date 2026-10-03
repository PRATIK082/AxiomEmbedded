# Connecting AI clients to AxiomEmbedded

One platform, five interfaces. Pick the row for your client; the SDK is the
single implementation behind all of them, so behavior is identical everywhere.

| Client | Recommended interface | Wiring |
|--------|----------------------|--------|
| Claude-based agent (Claude Code, API) | MCP | `claude mcp add axiom -- python -m axiom_cli mcp` (run from repo root), or paste `clients/mcp.json` entry into settings |
| OpenCode | MCP | Add the `clients/mcp.json` server block to `opencode.json` (`"mcp"` section); tools `engage`, `run_plan`, `read_skill` appear automatically |
| GPT-based agent (Codex CLI, API) | MCP or REST | Codex: MCP via config; API agents: `POST 127.0.0.1:8765/v1/run` after `python -m axiom_cli serve` |
| Gemini-based agent | MCP or REST | MCP server entry from `clients/mcp.json`; REST fallback as above |
| GitHub Copilot (VS Code) | MCP | `.vscode/mcp.json`: copy `clients/mcp.json`; see `clients/COPILOT.md` |
| Cursor-style IDE | MCP | Cursor Settings → MCP → add `clients/mcp.json` entry; see `clients/CURSOR.md` |
| VS Code (any extension) | MCP or Python SDK | MCP as above, or `from packages.axiom_sdk import engage, run_plan` in-repo |
| Custom AI / agent framework | A2A or Python SDK | `GET /.well-known/agent.json` for the agent card, `POST /v1/a2a/tasks`; or import the SDK |
| Local LLM (Ollama, llama.cpp) | REST or CLI | Serve once, call `/v1/run` from your runner; CLI `axiom engage/run` for scripts |
| Web application | REST | `/v1/skills`, `/v1/engage`, `/v1/run` — see `docs/client-matrix.md` |
| CLI / scripts | CLI | `python -m axiom_cli engage|run|mcp|serve` |

Tools exposed over MCP: `engage`, `run_plan`, `read_skill`, `list_skills`,
`list_profiles`. REST mirrors them at `/v1/*`; A2A wraps `run_plan` in a task
envelope at `/v1/a2a/tasks`.

Approval gates apply on every interface: plans list `approval_required_for`
and no interface executes pushes, releases, destructive commands, or
safety/security-critical changes without recorded human approval
(`configs/project.yaml`).
