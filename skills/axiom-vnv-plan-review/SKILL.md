---
name: axiom-vnv-plan-review
title: V&V Plan Review
description: >
  Use when an independent review of a V&V plan and trace matrix is required.
  Trigger phrases include "review test plan", "audit traceability matrix", and
  "check verification coverage".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.assurance.vnv_plan_review
  domain: industrial
  subdomain: assurance
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, review, verification]

  related_skills: [axiom-vnv-plan]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]

  lifecycle: [verification, validation]
  standards: ["ISO 12100:2010", "ISO 13849-2:2012", "ISO/TS 15066:2016", "IEC 62061:2021"]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: false
  safety_critical: false
  inputs: [vnv-plan artifact, safety-requirements artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom V&V-Plan Review (reviewer)

## Purpose
Independently review the V&V plan and trace matrix for requirement coverage
and result honesty, without modifying the source.

## Workflow
1. Read target and requirements artifacts; never edit them.
2. Verify every requirement maps to a test or an explicit open item.
3. Flag any pass claim without evidence as a Blocker.
4. Classify findings; run the review checker.

## Acceptance
- Validates against `schemas/assurance-review.schema.json`.
- Orphan requirements and unevidenced passes are Blockers.
- Draft evidence; qualified human review required.






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.





## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | ISO 12100:2010 | MEDIUM |
| R2 | ISO 13849-2:2012 | MEDIUM |
| R3 | ISO/TS 15066:2016 | MEDIUM |
| R4 | IEC 62061:2021 | MEDIUM |


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

