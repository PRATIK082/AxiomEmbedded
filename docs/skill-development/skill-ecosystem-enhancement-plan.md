# Skill Ecosystem Enhancement Plan (All Skills) — v2

**Branch:** feat/embedded-skills-intelligence-initiative
**Approach:** Phased, approval-gated, multi-agent (researcher → gap-finder → planner → implementer → validator).

## Phase 0 — Discovery (done)
Inventory complete (200 skills, 30 agents, 10 workflows, 10 profiles, 13 rules, registries, evaluation).

## Phase 1 — Research (done)
External skill ecosystems + AI-agent skill design/automation research captured in subagent reports.

## Phase 2 — Gap analysis (done)
`docs/skill-development/skill-ecosystem-gap-analysis.md`.

## Phase 3 — Plan (this document)
Approval checkpoint: present this plan before bulk implementation.

## Phase 4 — Implementation batches

### Batch F0: Framework hardening (P0)
1. Validator: manifest.yaml validation + version parity (catalog vs SKILL.md vs manifest).
2. Validator: require contract fields (inputs, outputs, risk_level, review_required, safety_critical, lifecycle, artifact_types, related_skills) for maturity >= beta.
3. Validator: description quality lint (third-person, 1-1024 chars, what+when, no vague terms, no first person).
4. Validator: progressive disclosure lint (body <=500 lines, references one level deep).
5. Validator: safety gating (safety_critical => review_required true).
6. Validator: maturity ladder enforcement (production requires tests+docs+examples+acceptance+>=3 evals).
7. Runner: propagate checker failures to status; plan-validate-execute mode; run-manifest schema validation; safety gate enforcement.
8. Pipeline: run per-skill tests; JSON schema validation of catalog.yaml.
9. create_skill: auto catalog registration; fix version mismatch; facet parity.
10. Engage/search: filter enabled; add maturity/group filters.
11. Group hygiene: coverage + orphan checks in CI.
12. Lints: naming convention (axiom-<domain>-<capability> or documented exception), forward-slash paths, descriptive file names.

### Batch F1: New meta-skills adoption (P1)
Adopt from external ecosystems (original content, Apache-2.0), each with SKILL.md + manifest + checklist + scripts/tests:
- axiom-skill-creator (with eval loop + description optimization)
- axiom-mcp-builder
- axiom-tool-schema-design
- axiom-agent-evaluation
- axiom-agent-observability
- axiom-human-in-the-loop
- axiom-multi-agent-orchestration
- axiom-prompt-injection-defense
- axiom-agent-red-teaming
- axiom-skills-purge (catalog hygiene)
- axiom-diagnosing-bugs
- axiom-improve-codebase-architecture
- axiom-clean-ai-slop
- axiom-git-commit-plan
- axiom-code-explainer
- axiom-agents-md-generator
- axiom-api-design
- axiom-cto-advisor
- axiom-security-best-practices
- axiom-security-threat-model
- axiom-security-ownership-map
- axiom-mcp-security-testing
- axiom-doc-coauthoring
- axiom-document-skills (pdf/docx/xlsx/pptx)
- axiom-frontend-design
- axiom-context-engineering
- axiom-skill-seekers (doc→SKILL conversion)

### Batch F2: Enhancement backfill (P2)
- Backfill contract fields across all 200 skills (automated where missing, defaults by domain).
- Convert checklists to YAML gate schema + add scripts/validate.py scaffold to production skills.
- Add eval harness (packages/eval) + require >=3 evals for production.
- Extend run manifest schema + autonomy KPI metrics.
- Add provenance field (metadata.source) to manifest schema.
- Add deprecation/superseded lifecycle state.
- Add rule files for skill contract/description/PD/eval/provenance.

### Batch F3: Coverage expansion (P3)
- Deepen aerospace (currently 1 skill) and cross-domain (1 skill).
- Add cloud/infra, data/ML, web/frontend, mobile, testing, documentation, observability, compliance-automation domains.
- Add EV-embedded-* evaluation tasks.
- Add agents: skill-evaluation, skill-adoption, documentation-generation, cloud-infra, data-ml.
- Add workflows: skill-adoption-import, skill-evaluation-run, skill-catalog-release.
- Add profiles: cloud-embedded, data-ml-embedded.
- Registry drift fixes (agents/profiles/workflows/platforms).

### Batch F4: Validation & evidence
- Run skill_pipeline.py --check, pytest, doctor, repo validate, compileall.
- Run new eval harness.
- Update tests expected counts.
- Update docs (AUTHORING_GUIDE, GROUPS, SKILL_FRAMEWORK).
- Evidence artifacts under artifacts/.

## Phase 5 — Validation
As above; no merge without green gates. No remote push without approval.

## Phase 6 — Review & PR
Final report; human approval for merge/push.

## Risks
- Scope creep: 200 skills; backfill must be automated and incremental.
- Generated-file drift: always use pipeline apply, never hand-edit generated.
- Safety: never bypass gates.
- License: all new content original Apache-2.0; provenance recorded.

## Approval checkpoint
Proceed with Batch F0 + F1 (framework + adoption) first, then F2, then F3? Or all at once? Recommend F0+F1 first, validate, then F2, then F3.
PY