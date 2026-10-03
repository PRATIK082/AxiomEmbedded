# Cursor wiring

1. Cursor Settings → MCP → Add new MCP server; paste the `axiom` entry from
   `clients/mcp.json` (command `python`, args `-m axiom_cli mcp`,
   cwd = absolute repo path).
2. Verify the five tools appear in the MCP tool list.
3. Prompt pattern: "Call axiom `run_plan` with my request first; follow the
   returned `phases` and load `context_files` before editing."

Cursor's codebase indexing stays as-is; Axiom supplies the skill slice and the
plan so the model works from `SKILL.md` context instead of guessing.
