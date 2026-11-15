# AxiomEmbedded Domain Engineering Skill Architecture (DESA) — Implementation Plan

## Status

Phase 0 (Audit) and Phase 1 (Taxonomy) are in progress. This document tracks
the staged implementation of the DESA restructuring recommended in the
repository review.

## Phase 0 — Audit (In Progress)

### Skill count correction

- Actual skill count: 259 (197 `axiom-*` + 62 legacy).
- Corrected stale references in:
  - `README.md` (was "35 new + 58 existing")
  - `docs/SKILL_FRAMEWORK.md` (was 88)
  - `docs/skills/CATALOG.md` (was 88)

### Deliverables completed

- `taxonomies/activities.yaml` — 30 engineering activities across 12 families
- `taxonomies/skill-types.yaml` — 7 capability kinds
- `taxonomies/relationship-semantics.yaml` — 16 relationship types with semantics
- `schemas/skill.schema.json` — expanded with DESA facets
- `standards/registry.yaml` — 24 standards with lifecycle state
- `domains/{automotive,aerospace,industrial,robotics}/domain-profile.yaml` — domain profiles
- `domains/{automotive,aerospace,industrial,robotics}/skill-family-map.yaml` — activity-to-skill mapping
- `docs/skill-development/contribution-lifecycle.md` — 9-stage contribution process
- `.github/ISSUE_TEMPLATE/skill_change.yml` — skill change request template
- `.github/PULL_REQUEST_TEMPLATE.md` — skill change PR template

## Phase 1 — Taxonomy (In Progress)

### Domains
16 domains defined in `taxonomies/domains.yaml` (existing).

### Activities
30 activities defined in `taxonomies/activities.yaml` across 12 families.

### Capability kinds
7 kinds defined in `taxonomies/skill-types.yaml`.

### Relationship semantics
16 relationship types defined in `taxonomies/relationship-semantics.yaml`.

## Phase 2 — Metadata and validation (Planned)

- [ ] Extend `enrich_catalog_facets.py` to populate `activity`, `capability_kind`, `primary_domain`, `risk_class`, `lifecycle_phases`, `standard_ids` from skill metadata.
- [ ] Update `schemas/skill.schema.json` validation in `packages/skills/validator.py`.
- [ ] Add cross-file consistency checks (catalog <-> manifest <-> frontmatter).
- [ ] Add standard lifecycle validation (draft/pre-release must not replace published).
- [ ] Add domain separation test (automotive request must not load aerospace-only process).
- [ ] Add missing-context test (skill must ask for missing standard/ASIL/DAL/SIL/toolchain/hardware).

## Phase 3 — Contribution lifecycle (In Progress)

- [x] Contribution lifecycle document
- [x] Issue template
- [x] PR template
- [ ] Skill scaffolding script updates (extend `scripts/create_skill.py`)
- [ ] Review gates documentation
- [ ] Automated validation hooks

## Phase 4 — Representative skill families (Planned)

First batch for four reference domains (automotive, aerospace, industrial, robotics):
- Requirements analysis and allocation
- Coding guidelines
- Code review
- Functional safety
- Cybersecurity
- Standards applicability

Each family independently reviewed and tested before expansion.

## Phase 5 — Routing and groups (Planned)

- [ ] Add `activity` key support to group matcher
- [ ] Add domain filtering to `axiom engage`
- [ ] Update `configs/domain-routing.yaml` for activity-based routing

## Phase 6 — Evaluation (Planned)

- [ ] Cross-domain separation tests
- [ ] Task-based evaluation cases
- [ ] Hardware validation where available

## Phase 7 — Expansion (Planned)

- [ ] Add medical, rail, space, defense, energy, IoT, consumer, semiconductor, marine, telecom domains
- [ ] Audit and improve existing 259 skills in place

## Known limitations

- Existing 259 skills have not been reclassified yet; their `axiom.subdomain` is mostly "legacy".
- Domain skill-family-maps list mostly "planned" skills.
- Standards registry is new; existing `standards/` YAML files still use minimal metadata.
- Group matcher does not yet support `activity` key.
- No automated domain separation or missing-context tests yet.

## Next steps

1. ~~Run `python scripts/skill_pipeline.py --check` to verify no breakage.~~ DONE — PASS (261 skills).
2. ~~Packaging foundation (pip + npm) and readiness skills.~~ DONE — `package.json` + `bin/axiom.js` + `tests/test_packaging.py`; `axiom-production-readiness` + `axiom-deployment-readiness`; `agents/release` owns both verdicts.
3. Implement Phase 2 metadata enrichment (populate DESA facets from skill metadata).
3. Begin Phase 4 with automotive requirements analysis skill family.
4. Update remaining domain profiles for the other 12 domains.
