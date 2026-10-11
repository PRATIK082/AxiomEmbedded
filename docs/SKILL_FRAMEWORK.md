# Axiom Skill Framework

Production-grade, reusable, extensible skill framework for AxiomEmbedded.
All content is original; no reference-repository text was used.

## Layout
- `skills/catalog.yaml` — every skill (88): axiom-* workflow skills + legacy skills.
- `skills/registry.yaml` — light index (dotted name, path, domain, maturity).
- `skills/<id>/SKILL.md` — contract: legacy frontmatter
  (`name, description, version, domains, platforms`) + `axiom:` block
  (dotted_name, domain, subdomain, category, maturity, tags, related_skills,
  lifecycle, standards, artifact_types, mcp_tools, risk_level, review_required,
  safety_critical, inputs, outputs, required_tools, optional_tools,
  checklists/templates/scripts refs).
- `skills/<id>/manifest.yaml` — packaging facets (keeps `test_skills_packaging` green).
- `skills/_templates/` — SKILL/checklist/test-plan/traceability/script templates.
- `packages/skills/{registry,loader,validator,runner}.py` — framework core.
- `scripts/{validate_skills,create_skill,scaffold_axiom_skills,extend_catalog,sync_skill_index}.py`.

## Commands / tools
- CLI: `axiom skills list|validate|search|run|report|create|apply`
  (`run`/`create` are dry-run unless `--apply`).
- MCP: `search_skills, validate_skill, run_skill, create_skill`
  (+ existing `list_skills`, `read_skill`).
- Runs produce manifests under `.axiom/runs/<timestamp>/<skill-id>/`
  (skill, version, timestamp, inputs, tools, decisions, files, warnings, checks).

## Maturity
experimental (28 scaffolds) → beta (2 exemplars: bsw-integration, uds) →
production only with validation + tests + docs + examples + acceptance process.

## Rules
- Never claim certification/compliance from heuristic checks.
- Safety/security output requires human review. No secrets, no unsafe shell,
  no unvalidated paths, no network calls.
