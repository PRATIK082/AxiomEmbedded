# Skill Manifest Decision (manifest.json vs SKILL.md header)

## Question
Should skills ship a `manifest.json` (agent-style, as in the
`automotive-cockpit` example) or is the SKILL.md frontmatter header enough?

## Decision
**SKILL.md frontmatter is the single source of truth. `manifest.json`
is a derived export, generated on demand, never stored.**

## Why (grounded in this repo)
- `tests/test_skills_packaging.py` enforces the SKILL.md frontmatter contract.
- `scripts/sync_clients.py` (`load_skills`) reads SKILL.md frontmatter as the
  single source for every CLI-agent client mirror
  (.opencode/.claude/copilot/GEMINI). Storing a second hand-written manifest
  would drift (this is exactly what the sync freshness gate guards against).
- Only `agents/` use `manifest.json`, because `AGENT.md` files carry no
  frontmatter contract -- the opposite situation from skills.
- `packages/skills/engage.py` discovers via `registries/skill-index.json`,
  itself synced from SKILL.md.

## The export (user's shape, plus axiom extras)
`axiom skills manifest <id>` / MCP `skill_manifest` / SDK `skill_manifest()`
emit exactly the requested keys -- `id, version, applicable_domains,
applicable_platforms, capabilities, category, evidence, inputs, outputs` --
plus `derived_from` (provenance) and an `axiom` object (dotted_name,
maturity, extends, related_skills, sub_skills, overlays, tools).
Drift is impossible by construction (generated, not stored) and covered by
`test_manifest_matches_frontmatter_all_skills`.

## Linking model (no duplicates)
- Existing `automotive-*` skills are **bases**; new `axiom-*` skills are
  **specializations** (`extends`), grouped as `sub_skills`, cross-referenced
  via `related_skills` (incl. siblings).
- Single source: the skill graph lives directly in `skills/catalog.yaml`
  entries, edited via `axiom skills link --set` (SDK `link_skill`, MCP
  `link_skill`). The validator enforces existence + related-symmetry as
  hard errors, so no derivation step can drift.
- Future tools/sub-skills/steps/requirements: `skills link --set`
  (`related_skills|extends|sub_skills|domain_overlays|platform_overlays`), `required_tools`/`mcp_tools` in the
  SKILL.md `axiom:` block (validated against the live MCP registry), and
  `domain_overlays`/`platform_overlays` (validated against `domains/`,
  `platforms/`). Docs: `docs/skills/AUTHORING_GUIDE.md`.
