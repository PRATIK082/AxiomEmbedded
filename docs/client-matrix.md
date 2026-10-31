# Client x interface matrix

| Client | MCP | A2A | REST | CLI | Python SDK |
|--------|-----|-----|------|-----|------------|
| Claude (Code / Agent) | [OK] `clients/mcp.json` | via REST | [OK] `/v1/*` | [OK] | [OK] |
| OpenCode | [OK] `clients/mcp.json` | via REST | [OK] | [OK] hooks/commands | [OK] |
| Codex (CLI) | -- | via REST | [OK] | [OK] terminal | [OK] |
| Antigravity | [OK] `clients/mcp.json` | via REST | [OK] | [OK] | [OK] |
| Muse | [OK] MCP config | via REST | [OK] | [OK] terminal | [OK] |
| Cursor | [OK] `clients/mcp.json` | via REST | [OK] | [OK] terminal | [OK] |
| VS Code (MCP ext.) | [OK] `clients/mcp.json` | via REST | [OK] | [OK] integrated terminal | [OK] |
| Custom AI agent | [OK] stdio JSON-RPC | [OK] `/v1/a2a/tasks` | [OK] | [OK] subprocess | [OK] direct import |
| Local LLM harness | -- | -- | [OK] localhost | [OK] | [OK] direct import |
| Web app | -- | [OK] agent card `/.well-known/agent.json` | [OK] | -- | -- |
| CLI / CI user | -- | -- | [OK] | [OK] `axiom engage/run/mcp/serve` | -- |

Agreement guarantee: one implementation (`packages/axiom_sdk`) sits behind all
five interfaces; `tests/test_interfaces.py` asserts SDK/CLI/MCP/REST/A2A return
the same automotive/mcu slice (42 skills).
