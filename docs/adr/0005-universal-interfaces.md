# ADR-0005: Universal client interfaces over one SDK

Date: 2026-10-03. Status: accepted.

## Context

After ADR-0004 (packaging: frontmatter, facets/index, `engage`, `run`,
multi-harness install), skills were consumable by file-aware harnesses only.
Requested clients — Copilot, OpenCode, Claude/GPT/Gemini agents, Cursor,
VS Code, custom AI, local LLM, web app, CLI — need protocol surfaces, not
just files. A prior build of this layer was lost (only `__pycache__` survived);
this ADR rebuilds it against the committed tree.

## Decision

One implementation, five interfaces, zero new dependencies (stdlib + PyYAML):

- `packages/axiom_sdk` — `engage_skills`, `run_plan`, `read_skill`,
  `list_skills`, `list_profiles`. Single source of truth.
- `packages/axiom_mcp/server.py` — newline-delimited JSON-RPC 2.0 over stdio;
  tools `engage`, `run_plan`, `read_skill`, `list_skills`, `list_profiles`.
- `packages/axiom_server/server.py` — `ThreadingHTTPServer`: `GET /v1/skills`,
  `/v1/skills/{id}`, `/v1/profiles`, `/.well-known/agent.json` card;
  `POST /v1/engage`, `/v1/run`, `/v1/a2a/tasks` (task envelope).
- CLI: `axiom mcp` (stdio server), `axiom serve --port` (default 8931).
- Clients: `clients/mcp.json`, `clients/COPILOT.md`, `clients/CURSOR.md`
  (also covers VS Code/Claude/OpenCode/Codex), `docs/client-matrix.md`.

## Consequences

- All interfaces agree by construction; `tests/test_interfaces.py` proves it
  on the automotive/mcu slice.
- No new runtime dependencies; `pyproject.toml` unchanged.
- Approval gate unchanged: `run_plan` plans only; execution needs human
  approval per `configs/project.yaml`.
