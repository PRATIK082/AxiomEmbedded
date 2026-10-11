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
   then `python -m axiom_cli skills apply` (regenerates index + mirrors).
7. Run: `python -m axiom_cli skills run <id> --objective "..."` (dry-run),
   `--apply` to write under `.axiom/runs/`.
8. Finish with the pipeline: `python -m axiom_cli skills apply` (one command:
   enrich → index → clients → validate). Never hand-edit generated files.
9. Grouping: new skills join groups automatically via id/subdomain/tags rules
   (see `docs/skills/GROUPS.md`). If your skill matches no group, widen a rule
   or add one — CI enforces 100% coverage.

## Linking (no duplicates, future tools/sub-skills/steps)
- New skill specializing an existing one? Edit the graph directly in
  `skills/catalog.yaml` — no second file:
  `axiom skills link --set related_skills <id> <others>...`
  (or `extends` with one base, `sub_skills`, `domain_overlays`,
  `platform_overlays`). Related back-links are auto-maintained.
  Same call over MCP: `link_skill`. Then `axiom skills apply` to
  propagate + validate (existence and related-symmetry are hard errors).
- Link tools via the `axiom:` block: `required_tools`, `optional_tools`,
  `mcp_tools` (checked against the live MCP registry at validation time;
  unknown names warn with a pointer to `docs/mcp-tool-backlog.md`).
- Link domain/platform packages via `domain_overlays` / `platform_overlays`
  in the catalog entry (must match a directory under `domains/` / `platforms/`).
- Custom steps/requirements: add them to the SKILL.md Workflow/Inputs
  sections and mirror machine-checkable gates in `checklists/` + `scripts/`.
- Consumers needing JSON: `axiom skills manifest <id>` (derived, never
  stored — see `docs/skill-manifest-decision.md`).
