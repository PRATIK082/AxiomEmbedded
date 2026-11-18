# DESA Review Gates

## Purpose
Every skill change (new, modified, reclassified) passes explicit review gates
before merge. Gates are enforced by CI (`skill_pipeline.py --check` +
`validate_all`) and by the pre-commit hooks in `.pre-commit-config.yaml`.

## Gates

### G1 — Schema and contract
- `SKILL.md` frontmatter parses; required keys present (`name` == directory).
- `manifest.yaml` exists; `id` matches directory; `version` matches frontmatter.
- `contract_version` present.

### G2 — Catalog and index consistency (errors, not warnings)
- Skill registered in `skills/catalog.yaml` with required fields.
- No duplicate ids; related/sub-skill/extends links resolve; no cycles.
- Present in `registries/skill-index.json` (unindexed skills fail validation).

### G3 — DESA facets
- `activity` is a known key in `taxonomies/activities.yaml`.
- `capability_kind` is a known key in `taxonomies/skill-types.yaml`.
- `standard_ids` resolve against `standards/registry.yaml`; draft/pre-release
  standards must not replace a published edition (warning, reviewer confirms).

### G4 — Production grade (strict for beta/production maturity)
- `tests/` non-empty, `scripts/validate.py` present, `references/` non-empty,
  `checklists/` non-empty. Description 40–1024 chars, no vague openers.
- `SKILL.md` body within progressive-disclosure limits.

### G5 — Independent review (one-branch-per-skill)
- Phase 4+ skill families land on dedicated branches, one branch per skill.
- Reviewer checks evidence (pipeline output, test results) — never accepts a
  PASS claim without artifacts. Verdicts: APPROVED / CHANGES_REQUIRED / BLOCKED.

## Automated hooks
- `pre-commit`: `skill_pipeline.py --check` + fast pytest subset run on every commit.
- Nightly: full `pytest -q` + `axiom_cli doctor` equivalent where runnable.
