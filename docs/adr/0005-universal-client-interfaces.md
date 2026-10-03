# ADR-0005: Universal client interfaces (MCP / A2A / REST / CLI / SDK)

Status: accepted · Date: 2026-10-03 · Relates: ADR-0004 (packaging v1.2.0)

## Context

Users invoke the platform from 11+ clients (Copilot, OpenCode, Claude/GPT/
Gemini agents, Cursor, VS Code, custom AI, local LLMs, web apps, CLI).
Client-specific integrations would fragment behavior and multiply maintenance.

## Decision

Expose exactly five interfaces, all backed by one implementation
(`packages/axiom_sdk`, stdlib-only, no new dependencies):

1. **MCP over stdio** (`packages/axiom_mcp/server.py`, `axiom mcp`) — newline-
   delimited JSON-RPC 2.0, tools `engage/run_plan/read_skill/list_skills/
   list_profiles`. No `mcp` package dependency by design (dependency freeze).
2. **REST** (`packages/axiom_server/server.py`, `axiom serve`) — `/v1/*`
   routes mirroring the SDK.
3. **A2A tasks** (same server) — agent card + `{taskId, status, artifact}`
   envelope around `run_plan`.
4. **CLI** (`axiom engage|run|mcp|serve`) — scripts and local-LLM runners.
5. **Python SDK** — direct import for in-repo and backend use.

## Consequences

- Behavior is identical on every client by construction; tests assert SDK/CLI/
  MCP/REST/A2A agreement on the automotive/mcu slice.
- Approval gates travel inside every plan payload; clients cannot bypass them
  through a thinner interface.
- Client quirks live in `clients/` docs, never in platform code.
