---
name: requirements-traceability
description: >
  CI orphan checks, suspect triage, and matrix hygiene. Use when automating
  trace maintenance in pipelines.
version: 1.2.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.requirements-traceability
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: [axiom-interface-contract-design]
  checklists: [checklists/requirements-traceability-checklist.md]

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
# Requirements-Traceability skill

Operational practice for maintaining the traceability chain day to day:
tooling workflows, link maintenance in fast-moving development, and the
traceability audits that keep `traceability` policy alive in practice.

## 1. Purpose and scope

**Purpose.** Keep the link chain (`sys_req -> sw_req -> code -> test -> evidence`)
current across sprints, branches, and parallel teams -- policy is set by
`traceability`; this skill runs the machinery.

**In scope.** Requirements-tool workflows, in-IDE link creation, CI checks for
orphans/suspects, branch/merge handling of trace data, metrics dashboards, and
pre-audit trace reviews.

**Non-goals.** Traceability policy and link semantics (see `traceability`).
Starts where policy ends: daily execution.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 29148 | 2018 | Traceability maintenance through requirement change | `https://www.iso.org/standard/72089.html` |
| 2 | ISO 26262-8 | 2018 | Clause 6 requirements management incl. traceability upkeep | `https://www.iso.org/standard/68390.html` |

## 3. Operating rules

1. **Link in the workflow, not after.** Definition-of-done for any story/task
   includes its trace links; CI rejects merge requests with new unlinked
   artifacts (automate the check from `schemas/traceability-matrix.schema.json`).
2. **Suspect triage daily.** The suspect-link queue from `traceability` S4 is
   triaged in stand-up cadence: re-verify, re-link, or escalate -- never older
   than one sprint.
3. **Branch strategy.** Trace data branches with code; merges reconcile link
   conflicts explicitly (both-sides-changed links re-reviewed, not
   auto-resolved).
4. **Metrics visible.** Dashboard tracks: orphan count, suspect count and age,
   link depth (requirements reaching evidence), and audit-sample pass rate.
   Trends reviewed at each iteration boundary.

## 4. Pre-audit review (blocking before assessment)

1. Orphan/suspect counts at zero with tool evidence.
2. Link-depth metric: 100% of safety requirements reach evidence.
3. Sample review of newest links for granularity conformance.
4. Dashboard trend stable or improving across the last two iterations.

## 5. Verification of this skill (Phase 4 gate)

- CI orphan/suspect check exists and is enforced (show a blocked merge or
  it does not exist).
- Metrics history present, not a single snapshot.






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

