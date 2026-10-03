# AxiomEmbedded for Cursor / VS Code / Claude / OpenCode / Codex

All five clients consume the same three surfaces — pick one:

| Surface | Setup | Best for |
|---------|-------|----------|
| MCP stdio | point the client at `clients/mcp.json` (`python -m axiom_cli mcp`) | Claude, Cursor, VS Code MCP, OpenCode |
| CLI | `python -m axiom_cli engage/run` in terminal or hooks | Codex, custom agents, CI |
| REST/A2A | `python -m axiom_cli serve --port 8931` | web apps, services, remote agents |

## Suggested flow (any client)

1. `engage` with the project's domain + platform (e.g. automotive + mcu).
2. Load only the returned `context_files` — never the whole repo.
3. `run_plan` for the task; present the plan; execute only after approval.
4. Verify per the skill's Phase 4 gate; record evidence.

## Python SDK (custom AI / local LLM harness)

```python
from packages import axiom_sdk
sel = axiom_sdk.engage_skills("automotive", "mcu")   # 42 skills
plan = axiom_sdk.run_plan("add watchdog supervision", "automotive", "mcu")
```

The SDK is the single implementation behind MCP, REST, A2A, and CLI —
all five always agree (proven by `tests/test_interfaces.py`).
