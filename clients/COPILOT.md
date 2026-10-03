# GitHub Copilot wiring

Copilot in VS Code speaks MCP. No extension code needed.

1. Copy `clients/mcp.json` to your workspace as `.vscode/mcp.json`,
   replacing `<ABSOLUTE-PATH-TO-AxiomEmbedded>` with the repo path.
2. VS Code discovers the `axiom` server; Copilot's agent mode lists the
   tools (`engage`, `run_plan`, `read_skill`, `list_skills`, `list_profiles`).
3. Prompt pattern: "Use the axiom `engage` tool for domain automotive,
   platform mcu, then load the returned context files before planning."

Alternative without MCP: point Copilot at the repo and reference
`docs/using-skills.md` + `python scripts/install_skills.py` output so skills
are plain workspace files it already reads.
