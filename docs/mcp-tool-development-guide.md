# MCP Tool Development Guide

- Single implementation in `packages/axiom_sdk`; thin wrappers in
  `axiom_mcp/server.py` (TOOLS dict) and `axiom_cli/main.py`.
- Typed `inputSchema` (see `_schema`/`_str_prop` helpers); structured JSON
  result + human-readable `summary` where applicable.
- Write-capable tools default to dry-run (`apply=false`); writes restricted
  to `skills/` (create) or `<output>/.axiom/runs/` (run).
- Security: skill-id allowlist `^[a-z0-9-]+$`, repo-relative paths only
  (reject absolute/`..`), no secrets in logs, no shell, no network.
- Determinism: sorted outputs; timestamps only in run manifests.
- Tests per tool: schema, negative (bad id, traversal, missing skill),
  golden-file for report shapes. See `tests/test_skill_framework.py`.
- Backlog/spec format: `docs/mcp-tool-backlog.md`.
