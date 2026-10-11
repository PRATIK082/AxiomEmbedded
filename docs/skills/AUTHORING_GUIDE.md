# Skill Authoring Guide

1. Scaffold: `python scripts/create_skill.py --id axiom-<domain>-<cap> --title "..." --apply`
   (dry-run without `--apply`).
2. Fill SKILL.md from `skills/_templates/SKILL.template.md` — every section,
   real workflow, real decision rules, real failure modes.
3. Add `checklists/review.yaml`, at least one template, deterministic `scripts/`
   (stdlib-only preferred), `tests/` for scripts.
4. Mark maturity honestly: experimental until proven.
5. Validate: `python scripts/validate_skills.py --skill <id>` then full run.
6. Register: add to `skills/catalog.yaml` (or re-run scaffold/extend scripts),
   then `python scripts/sync_skill_index.py`.
7. Run: `python -m axiom_cli skills run <id> --objective "..."` (dry-run),
   `--apply` to write under `.axiom/runs/`.
