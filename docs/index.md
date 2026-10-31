# AxiomEmbedded

Domain-neutral embedded engineering platform: Tab-selectable specialist
agents, a domain/platform skill graph, MCP + CLI + REST interfaces, and an
evidence-first workflow.

- **Install:** `uv tool install axiom-embedded` (or `pipx install`) --
  see [Install](ecosystem/install.md).
- **Independence plan:** [standalone-independence.md](ecosystem/standalone-independence.md).
- **Domain-aware agents:** [domain-aware-execution.md](agents/domain-aware-execution.md).

Quick start:

```bash
axiom doctor
axiom engage --domain automotive --platform mcu
axiom mcp --check
axiom eval --list
```
