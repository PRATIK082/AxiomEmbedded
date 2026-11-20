---
name: axiom-hazard-risk-review
title: Hazard Analysis and Risk Assessment Review
description: >
  Use when an independent review of a hazard-risk artifact is required. Trigger
  phrases include "review hazard analysis", "audit risk assessment", and "check
  hazard coverage".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.assurance.hazard_risk_review
  domain: industrial
  subdomain: safety
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, review, safety]

  related_skills: [axiom-hazard-risk]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]

  lifecycle: [requirements, verification]
  standards: ["ISO 12100:2010", "ISO 10218-1:2011", "ISO 10218-2:2011", "ISO/TS 15066:2016", "ISO 13849-1:2023", "ISO 13850:2015", "ISO 14118:2017"]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: true
  safety_critical: true
  inputs: [hazard-risk artifact, system-scope artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Hazard-Risk Review (reviewer)

## Purpose
Independently review a hazard-risk artifact without modifying it, challenging
severity ratings, missing modes, and control adequacy.

## Workflow
1. Read target and scope artifacts; never edit them.
2. Copy `templates/review.template.yaml`; record target and reviewer.
3. Verify every high/critical hazard has a control or rationale; flag invented
   failure rates or missing modes.
4. Classify findings Blocker through Information Request with location,
   evidence, recommendation, and owner.
5. Run `scripts/check_review.py <report>`.

## Acceptance
- Validates against `schemas/assurance-review.schema.json`.
- Any Blocker forces verdict revise-and-resubmit.
- Draft evidence only; qualified human review still required. Not a
  certification verdict.






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
| R2 | ISO 10218-1:2011 | MEDIUM |
| R3 | ISO 10218-2:2011 | MEDIUM |
| R4 | ISO/TS 15066:2016 | MEDIUM |
| R5 | ISO 13849-1:2023 | MEDIUM |
| R6 | ISO 13850:2015 | MEDIUM |
| R7 | ISO 14118:2017 | MEDIUM |


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

