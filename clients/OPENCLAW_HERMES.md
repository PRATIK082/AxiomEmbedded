# AxiomEmbedded on OpenClaw / Hermes (manual MCP setup)

Status: supported via MCP runtime discovery. `axiom install --client`
does not yet cover these two clients: their config-file locations are
not verified against vendor docs in this repo, and unverified paths
are not shipped. This file gives the verified manual setup instead.

## What is verified (ground truth, re-checkable)

- Skill compatibility: `python scripts/audit_client_compat.py` checks
  every `skills/*/SKILL.md` for folder-model fit (`name == dirname`,
  slug `[a-z0-9-]{1,64}`, non-empty description). Current: 270/270 pass.
- MCP tool surface: 38 tools in `axiom_mcp/server.py`, including
  `search_skills`, `engage`, `read_skill`, `run_skill` -- skills resolve
  server-side, so no skill files need copying.
- Tests: `tests/test_openclaw_hermes.py` re-runs the audit and pins the
  server command below (fails on drift).

## Server entry (preferred)

```json
{"command": "axiom", "args": ["mcp"]}
```

Fallback when the `axiom` shim is not on PATH
(`pipx install axiom-embedded` recommended):

```json
{"command": "python", "args": ["-m", "axiom_cli", "mcp"]}
```

Register one of the above as server `axiom-embedded` in your
tool's MCP configuration, then confirm with `engage` or
`search_skills` before relying on skill access.

## Skill model fit

Axiom skills are folder + `SKILL.md` with optional YAML frontmatter
(`name`, `description`, `version`, `domains`, `platforms`, `axiom`
block) -- the same shape folder-model tools consume. The audit above
is the compatibility gate: any skill failing it fails
`scripts/skill_pipeline.py --check` too.

## Installer support: pending, not shipped

`packages/installer.py` `CLIENTS` stays at the 10 verified clients
until OpenClaw/Hermes config paths are confirmed against primary
vendor documentation. Guessing `~/.openclaw/...` locations would put
fabricated paths into production code; that is explicitly out of
scope until verified. Contributions welcome: add the vendor-doc
reference plus a `tests/test_install.py`-style parametrized case.
