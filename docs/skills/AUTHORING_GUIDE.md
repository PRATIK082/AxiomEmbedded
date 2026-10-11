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

## Linking (no duplicates, future tools/sub-skills/steps)
- New skill specializing an existing one? Set `extends: <base>` and add the
  pair to `skills/links.yaml`, then `python scripts/link_related_skills.py`
  (`--check` in CI; `--set related|extends|sub-skills <id> ...` for ad-hoc).
- Link tools via the `axiom:` block: `required_tools`, `optional_tools`,
  `mcp_tools` (checked against the live MCP registry at validation time;
  unknown names warn with a pointer to `docs/mcp-tool-backlog.md`).
- Link domain/platform packages via `domain_overlays` / `platform_overlays`
  in `links.yaml` (must match a directory under `domains/` / `platforms/`).
- Custom steps/requirements: add them to the SKILL.md Workflow/Inputs
  sections and mirror machine-checkable gates in `checklists/` + `scripts/`.
- Consumers needing JSON: `axiom skills manifest <id>` (derived, never
  stored — see `docs/skill-manifest-decision.md`).
