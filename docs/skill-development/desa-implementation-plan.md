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

## Phase 2 — Metadata and validation (In Progress)

- [x] Extend `enrich_catalog_facets.py` to populate `activity`, `capability_kind`, `primary_domain`, `risk_class`, `lifecycle_phases`, `standard_ids` from skill metadata.
- [x] Add DESA warning checks in `packages/skills/validator.py` (`desa_checks`: unknown activity/kind/standard, draft-must-not-replace-published).
- [x] Promote cross-file consistency checks (catalog <-> manifest <-> frontmatter) to errors (catalog-missing is error; unindexed fails verdict).
- [x] Add standard lifecycle validation (draft/pre-release must not replace published).
- [x] Add domain separation test (`tests/test_desa_phases.py`).
- [x] Add missing-context test (unknown activity returns warning envelope; draft standard warns).

## Phase 3 — Contribution lifecycle (In Progress)

- [x] Contribution lifecycle document
- [x] Issue template
- [x] PR template
- [x] Skill scaffolding script updates (extend `scripts/create_skill.py`)
- [x] Review gates documentation (`docs/skill-development/review-gates.md`)
- [x] Automated validation hooks (pre-commit: pipeline --check + fast subset; documented in review-gates)

## Phase 4 — Representative skill families (In Progress)

First batch for four reference domains (automotive, aerospace, industrial, robotics):
- Requirements analysis and allocation
- Coding guidelines
- Code review
- Functional safety
- Cybersecurity
- Standards applicability

Each family lands on its own review-gated branch (`feat/skill-<name>`)
per `workflows/embedded-skills-deep-update.yaml` v2 and `review-gates.md` G5.

### Automotive pilot — DONE (branch `feat/skill-axiom-automotive-requirements-analysis`)
- `axiom-automotive-requirements-analysis` (requirements-analysis; SWE.1 flow-down,
  SHALL-form, ASIL-from-safety-plan-only, traceability stubs, gap report).
- Reuse check first: only generic `requirements` engaged for
  automotive+requirements-analysis, so a new domain skill was justified.
- Pipeline --check PASS (262 skills); DESA suite 13/13 PASS.
- Awaiting review (APPROVED / CHANGES_REQUIRED / BLOCKED) before merge.

### Automotive remaining (each one branch per skill)
- [x] requirements-allocation — DONE (branch `feat/skill-axiom-automotive-requirements-allocation`; single-owner allocation, interface contracts, UNALLOCATED-with-rationale; 262 OK, DESA 13/13; awaiting review)
- [x] code-review — DONE (branch `feat/skill-axiom-automotive-code-review`; SWE.5/SWE.6 process review delegating rule checks to `axiom-misra-c-cpp-review`; validator + checklist + template + record validator + 2 skill tests; 262 OK, DESA 13/13, packaging 6/6; awaiting review)
- [x] functional-safety — DONE via reuse, no new skill (branch `feat/upgrade-automotive-safety-wiring`; `axiom-functional-safety` already deep ISO 26262 concept-phase: HARA/ASIL/SG/FSC/FSR + asil-table; upgrade = frontmatter `related_skills` wired to the 5 new DESA skills, maturity stays experimental; family-map nested activities for all 5 new skills set to existing + skill id; the 5 skill branches had their top-level map keys reverted to base so merges stay clean; pipeline 261 OK, DESA 13/13, packaging 6/6; awaiting review)
- [x] cybersecurity — DONE via reuse, no new skill (branch `feat/upgrade-automotive-security-wiring`, commit 2e7ab2f; `automotive-cybersecurity` already production ISO/SAE 21434 TARA concept-phase: item definition, TARA, CAL, security goals, R155/R156 case; upgrade = frontmatter `related_skills` wired to the 5 new DESA skills, fixed dangling family-map ref `axiom-automotive-cybersecurity` (nonexistent) to `automotive-cybersecurity`; pipeline 261 OK, DESA+packaging 19/19; awaiting review). NOTE: a prior session note claimed this done as commit 119a2c2 — that commit never existed in this repo (verified via reflog + remote); the work above is the real landing.
- [ ] safety-review / security-review (distinct from functional-safety/cybersecurity build skills)
- [x] standards-applicability — DONE (branch `feat/skill-axiom-automotive-standards-applicability`, commit b11b09f; applicability matrix with APPLICABLE/NOT_APPLICABLE/DEFERRED verdicts, lifecycle gate, matrix validator + 2 skill tests; pipeline --check 262 OK, DESA 13/13, packaging 8/8; awaiting review)
- [x] verification - DONE (branch `feat/skill-axiom-automotive-requirements-verification`; SWE.4/SWE.5/SWE.6 requirements-to-evidence closure, technique delegation, verdict record validator + 2 skill tests; pipeline 262 OK, DESA 13/13, packaging 6/6; awaiting review)
- [ ] unit/integration/system-testing, validation (bind to V-model + ASPICE SWE.4-6)
- [ ] configuration-management, release-readiness (bind to axiom release verdicts)
- [ ] debugging, documentation (domain-specific workflows)
- [ ] Upgrade-in-place (no new skill): automotive-coding,
      axiom-automotive-cybersecurity, axiom-automotive-architecture,
      axiom-automotive-spice — raise maturity through validation, not metadata.
      (axiom-functional-safety wiring DONE above; standard_ids normalization
      deferred as Phase 2 remainder — 99 catalog entries use human-readable
      standard names, needs registry-alias mapping, not per-skill fixes.)

### Other reference domains (aerospace, industrial, robotics)
- [x] Aerospace requirements-analysis — DONE (branch `feat/skill-axiom-aerospace-requirements-analysis`; ARP4754A system-to-HLR flow-down, DO-178C HLR characteristics, derived-requirement flagging, DAL-from-ARP4761-only; validator + checklist + template + record validator + 2 skill tests; 262 OK, DESA+packaging 19/19; awaiting review)
- [x] Aerospace requirements-allocation — DONE, verified real (branch `feat/skill-axiom-aerospace-requirements-allocation`, commit `95a4764`, pushed; ARP4754A/DO-178C single-owner allocation, UNALLOCATED-with-rationale, validator + 2 skill tests; DESA+packaging 19/19, pipeline 262 OK; awaiting review)
- [x] Aerospace code-review — DONE, verified real (branch `feat/skill-axiom-aerospace-code-review`, DO-178C verification-review process, DAL independence, verdict contract, 2 skill tests; DESA+packaging 19/19, pipeline 262 OK; awaiting review)
- [x] Aerospace verification — DONE, verified real (branch `feat/skill-axiom-aerospace-verification`, DO-178C verification-case/procedure/results closure, structural-coverage objectives, VERIFIED/FAILED/WAIVED verdict contract, 2 skill tests; DESA+packaging 19/19, pipeline 262 OK; awaiting review)
- [ ] Aerospace remaining: standards-applicability (industrial/robotics need allocation + verification each)
- [ ] Mirror the automotive batch per domain family map; reuse cross-domain
      skills (reviews, testing method) where the activity is domain-agnostic.

## Phase 5 — Routing and groups (In Progress)

- [x] Add `activity` (+`capability_kind`, `primary_domain`, `risk_class`) key support to group matcher
- [x] Add activity filtering to `axiom engage` (`--activity` flag; unknown activity returns explicit warning envelope)
- [x] Full-catalog activity inference (261/261 mapped via `enrich_catalog_facets.py` fallback map; 5516853)
- [x] Update `configs/domain-routing.yaml` for activity-based routing (`activity_routing` hints; engage is enforcement point)
- [ ] Add domain filtering to `axiom engage` (domain param filters index facets today; primary_domain narrowing deferred — generic skills must stay visible cross-domain)

## Phase 6 — Evaluation (In Progress)

- [x] Cross-domain separation tests (`tests/test_desa_phases.py`)
- [ ] Task-based evaluation cases
- [ ] Hardware validation where available

## Phase 7 — Expansion (Planned)

- [ ] Add medical, rail, space, defense, energy, IoT, consumer, semiconductor, marine, telecom domains
- [ ] Audit and improve existing 259 skills in place

## Known limitations

- Existing 259 skills have not been reclassified yet; their `axiom.subdomain` is mostly "legacy".
- Domain skill-family-maps list mostly "planned" skills.
- Standards registry is new; existing `standards/` YAML files still use minimal metadata.
- Group matcher supports `activity` (+`capability_kind`, `primary_domain`, `risk_class`); `axiom engage --activity` filters via the DESA activity map with an explicit warning envelope for unknown activities.
- Automated domain separation + missing-context tests exist (`tests/test_desa_phases.py`, 13 tests).

## Next steps

1. ~~Run `python scripts/skill_pipeline.py --check` to verify no breakage.~~ DONE — PASS (261 skills).
2. ~~Packaging foundation (pip + npm) and readiness skills.~~ DONE — `package.json` + `bin/axiom.js` + `tests/test_packaging.py`; `axiom-production-readiness` + `axiom-deployment-readiness`; `agents/release` owns both verdicts.
3. ~~Implement Phase 2 metadata enrichment (populate DESA facets from skill metadata).~~ DONE — facets + validator promotion + activity routing (7e90b34).
4. Phase 4 automotive batch: pilot DONE (awaiting review); work the remaining
   list above one-branch-per-skill in domain-map order.
5. Update remaining domain profiles for the other 12 domains.
