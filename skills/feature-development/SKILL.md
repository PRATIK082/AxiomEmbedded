---
name: feature-development
description: >
  Vertical slicing, short-lived branches, and tests-travel-with-code. Use when
  adding product features incrementally.
version: 1.2.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.feature-development
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: []
  checklists: [checklists/feature-development-checklist.md]

  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: []
  optional_tools: []
---
# Feature-Development skill

End-to-end delivery of a single feature through the V-model: from requirement
slice to merged, traced, tested increment -- without breaking the architecture
or the release.

## 1. Purpose and scope

**Purpose.** Give engineers a repeatable feature workflow that keeps scope
small, traceability intact, and merges safe on safety-relevant codebases.

**In scope.** Feature scoping and slicing, branch-per-feature workflow, design
notes and ADRs for feature decisions, implementation per `implementation`,
test pyramid per feature (unit -> integration -> system), feature flags and
conditional compilation, and merge readiness.

**Non-goals.** Portfolio planning and release trains (see `release`). Starts at
an approved requirement slice, ends at a merged, traced feature.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 12207 Life cycle processes | 2017 | Software implementation and integration processes | `https://www.iso.org/standard/63712.html` |
| 2 | ISO 26262-6 Software level | 2018 | Clauses 5-9: design, construction, verification per ASIL | `https://www.iso.org/standard/68388.html` |

## 3. Feature workflow rules

1. **Slice vertically.** Each feature delivers a thin end-to-end increment
   (requirement -> code -> test) in one merge; horizontal layers ("all drivers,
   no tests") are not mergeable units.
2. **Branch per feature, short-lived.** Branches live days, not months; rebase
   on `main` regularly. Stale branches accumulate silent conflicts -- the
   oldest open feature branch is a project metric reviewed weekly.
3. **Flags, not forks.** Incomplete features hide behind compile-time or
   runtime flags with a removal date; commented-out code and parallel
   implementations are defects.
4. **Tests travel with code.** The feature merge includes its unit,
   integration, and requirement-trace updates; "tests in a follow-up" is a
   blocking finding.
5. **Safety-relevant features** follow the integrity level's independence and
   review rules (`safety` S6) from the first commit, not retrofitted at merge.

## 4. Merge gates (blocking)

1. Requirement slice traced through code to tests in the matrix.
2. Static analysis clean; coverage target met for new code.
3. Reviews complete with dispositions; independence satisfied per ASIL/SIL/DAL.
4. No dead flags, no commented-out code, no TODO-without-issue.

## 5. Verification of this skill (Phase 4 gate)

- Standards carry number + version + clause + URL (S2).






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.



## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | (none declared) | LOW |


## Impact tiers

| Tier | Meaning |
|---|---|
| CRITICAL | Safety/security-critical; requires human approval and impact assessment |
| HIGH | Significant impact; requires review |
| MEDIUM | Moderate impact; standard review |
| LOW | Minor impact; routine review |

### Rule impact assignments

All rules in this skill default to MEDIUM unless marked CRITICAL or HIGH
in the rule ID -> clause map above.

## Deviation management

Any deviation must be recorded with: Rule ID, reason, file/location,
approver, and date. CRITICAL-rule deviations require safety-lead approval
and an impact assessment. Deviations are first-class artifacts, not comments.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.

