# Gap Analysis: current vs Axiom Skill Framework

| Area | Current | Required (prompts 1+2 combined) | Gap |
|---|---|---|---|
| Discovery | skill-index.json + skills.json, flat IDs | catalog.yaml + registry.yaml, axiom-* IDs, domain/lifecycle/standard/artifact/mcp-tool facets, maturity | No rich catalog; no maturity/enabled flags |
| Loading | engage.py facet match; read_skill reads SKILL.md+manifest | Safe frontmatter loader, field/version/tag/IO/file validation, external packs opt-in | No loader module |
| Execution | run/engage emit plans only | Structured runner: context in, run manifest out, .axiom/runs/<ts>/<skill>/, dry-run | No runner |
| Validation | test_skills_packaging frontmatter/manifest/index | SKILL.md syntax+frontmatter, referenced files, script tests, duplicate/circular checks | Partial; no validator module/CI |
| Authoring | Manual dirs + sync_clients | create_skill scaffold, validate_skills, list_skills, run_skill, skill_report | Missing commands/tools |
| Content | 58 flat skills; autosar + automotive-diagnostics deep | 30 axiom-* automotive/embedded skills, each with workflow+checklist+template+script+tests | 2 overlap, 28 new; contract upgrade needed |
| MCP | 21 tools (no skill CRUD) | list/get/search/validate/create/run + generators (report, checklist, test-plan, traceability, config review, trace analysis) | Missing skill tools |
| Observability | status dashboard | Run manifests, provenance sidecars, skill freshness | Missing |
| Versioning | manifest version 1.2.0/1.3.0 | Semver per skill + maturity experimental/beta/production | Missing policy |
| Testing | Packaging contract tests | Loader/registry/validator/runner unit + fixture + negative + golden-file tests | Missing |
| Docs | README, AGENTS.md, OPENCODE_* | SKILL_FRAMEWORK.md, AUTHORING_GUIDE, CATALOG, migration mapping, FINAL report | Missing |

## Overlaps/conflicts
- `autosar` ~ axiom-autosar-* family; `automotive-diagnostics` ~ axiom-diagnostics-*; `adas`, `automotive-networks`, `automotive-cybersecurity`, `safety`, `test-automation`, `rtos`, `robotics` overlap new skills. Resolution: keep existing skills (backward compat), add axiom-* as deeper workflow skills referencing existing ones; map in docs/migration/EXISTING_CAPABILITY_MAPPING.md.
- ID schemes: flat (`autosar`) vs `axiom-<domain>-<capability>` (prompt1) vs `axiom.<domain>.<skill>` (prompt2). Resolution: directory `axiom-<domain>-<capability>`, frontmatter `name: axiom-<domain>-<capability>` (kebab, filesystem-safe), `axiom.name` alias in dot form for prompt2 compat. Catalog stores both.
