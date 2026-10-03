# Client × interface matrix

| Client | MCP | A2A | REST | CLI | Python SDK |
|--------|-----|-----|------|-----|------------|
| Claude (Code / Agent) | ✅ `clients/mcp.json` | via REST | ✅ `/v1/*` | ✅ | ✅ |
| OpenCode | ✅ `clients/mcp.json` | via REST | ✅ | ✅ hooks/commands | ✅ |
| Codex (CLI) | — | via REST | ✅ | ✅ terminal | ✅ |
| Antigravity | ✅ `clients/mcp.json` | via REST | ✅ | ✅ | ✅ |
| Muse | ✅ MCP config | via REST | ✅ | ✅ terminal | ✅ |
| Cursor | ✅ `clients/mcp.json` | via REST | ✅ | ✅ terminal | ✅ |
| VS Code (MCP ext.) | ✅ `clients/mcp.json` | via REST | ✅ | ✅ integrated terminal | ✅ |
| Custom AI agent | ✅ stdio JSON-RPC | ✅ `/v1/a2a/tasks` | ✅ | ✅ subprocess | ✅ direct import |
| Local LLM harness | — | — | ✅ localhost | ✅ | ✅ direct import |
| Web app | — | ✅ agent card `/.well-known/agent.json` | ✅ | — | — |
| CLI / CI user | — | — | ✅ | ✅ `axiom engage/run/mcp/serve` | — |

Agreement guarantee: one implementation (`packages/axiom_sdk`) sits behind all
five interfaces; `tests/test_interfaces.py` asserts SDK/CLI/MCP/REST/A2A return
the same automotive/mcu slice (42 skills).
