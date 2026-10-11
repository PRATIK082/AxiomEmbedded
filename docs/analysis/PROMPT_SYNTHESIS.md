# Prompt Synthesis — Combining Prompt 1 (Skill Framework) and Prompt 2 (Skill Library Expansion)

Branch: `feature/automotive-skill-prompt1`. Both prompts were analyzed, deduplicated,
and merged into one workflow. No reference-repository text was used in either prompt's
implementation; all skills are original AxiomEmbedded content.

## 1. Deep analysis: what each prompt asks

| Concern | Prompt 1 (phases 1–10) | Prompt 2 (phases 1–6) | Verdict |
|---|---|---|---|
| Analysis docs | `docs/analysis/{CURRENT_STATE,GAP_ANALYSIS,INTEGRATION_PLAN}.md` | `docs/{current-state-assessment,skill-gap-analysis}.md` | Both exist; keep both, cross-link (different lenses: integration-risk vs coverage-gap) |
| Registry file | `skills/catalog.yaml`, ids `axiom-<domain>-<capability>` | `skills/registry.yaml`, names `axiom.<domain>.<skill>` | Keep both: catalog = rich record (prompt 1 fields + prompt 2 facets), registry = prompt 2 discovery shape. Skill dirs carry both: directory/`id` in dash form, `axiom.dotted_name` in dot form |
| Discovery facets | maturity/enabled/tags/inputs/outputs/dependencies | + lifecycle/standards/artifact_types/mcp_tools/risk_level/review_required | Enrich catalog entries from SKILL.md `axiom:` blocks (this branch: `scripts/enrich_catalog_facets.py`) |
| Skill body sections | Purpose…Guardrails…References | Purpose…Review Checklist…References | Superset section order adopted in `skills/_templates/SKILL.template.md`; validator requires Purpose/Workflow/Acceptance |
| 30 automotive/platform skills | 30 named skills, 2 beta exemplars first | 10 core automotive first, then expansion | Done on parent branch; this branch adds the 5 cross-domain skills prompt 2 names explicitly (contract, static-analysis triage, CI/CD, ADR, tech debt) |
| MCP tools | 13 named tools | tool backlog spec with schemas | 7 P1 wrappers implemented (`packages/skill_tools.py`, 33 tools); backlog doc updated |
| manifest.json | not required | example shape given | Derived export decision (`docs/skill-manifest-decision.md`): SKILL.md frontmatter is single source; `axiom skills manifest` + MCP `skill_manifest` emit that shape |
| Link to domain/platform/OS | implied | explicit: link skills to domain/platform/OS packages | `skills/links.yaml` (related/extends/overlays) + `packages/skills/registry.resolve_extends`; `domains`/`platforms` frontmatter keys drive `packages/skills/engage.py` matching |
| Extensibility | create/validate/list/run/report commands | authoring guide + quality gates | Both exist; this branch adds facet-parity enforcement so future edits stay consistent |

## 2. Combined workflow (single activity list)

1. Analyze repo + reference coverage (no copying) → gap table.
2. Framework core: catalog + registry + loader + validator + runner + dry-run.
3. Two exemplar deep skills first (bsw-integration, UDS), then scaffolds.
4. Link pass: legacy ↔ axiom-* (related/extends/overlays), no duplicates.
5. P1 tool wrappers with security policy (allowlist, repo-confined paths, dry-run default).
6. Facet parity: catalog mirrors SKILL.md `axiom:` blocks (this branch).
7. Cross-domain completion: contract, triage, CI/CD, ADR, debt (this branch).
8. Tests + CI + docs + changelog, then push + PR.

## 3. Naming decision (both prompts honored)

- Directory and catalog `id`: `axiom-<domain>-<capability>` (prompt 1).
- Catalog `name` and `axiom.dotted_name`: `axiom.<domain>.<skill>` (prompt 2).
- One skill, two keys, zero duplication; `skill_manifest` export carries both.

## 4. What this branch adds

- `scripts/enrich_catalog_facets.py` + facet-parity test.
- 5 cross-domain skills: `axiom-interface-contract-design`,
  `axiom-static-analysis-triage`, `axiom-embedded-cicd`,
  `axiom-architecture-decision-records`, `axiom-technical-debt-assessment`.
- links.yaml entries + index/catalog/registry sync for the 5.
- CHANGELOG entry.
