---
name: axiom-safety-requirements-review
title: Safety Requirements Review
description: 'Use when an independent review of safety requirements is required. Trigger
  phrases include "review safety requirements", "audit requirement coverage", and
  "check requirements traceability".

  '
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.assurance.safety_requirements_review
  domain: industrial
  subdomain: safety
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, review, requirements]

  related_skills: [axiom-safety-requirements]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]

  lifecycle: [requirements]
  standards: ["ISO 12100:2010", "ISO 13849-1:2023", "ISO 13850:2015", "ISO 14118:2017", "IEC 62061:2021", "IEC 61508:2010"]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: true
  safety_critical: true
  inputs: [safety-requirements artifact, hazard-risk artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Safety-Requirements Review (reviewer)

## Purpose
Independently review safety requirements for atomicity, verifiability, and
hazard coverage without modifying the source artifact.

## Workflow
1. Read target and hazard artifacts; never edit them.
2. Copy the review template; check each requirement for testability and
   verification method.
3. Flag vague language, missing hazard links, and invented verification claims.
4. Classify findings with owner and recommendation; run the review checker.

## Acceptance
- Validates against `schemas/assurance-review.schema.json`.
- Uncovered high/critical hazards are Blockers.
- Requires qualified human review; not a conformity approval.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| safety-req-review-atomicity | IEC 62061:2021 Cl. 6 | HIGH |
| safety-req-review-hazard-coverage | ISO 12100:2010 Cl. 6 | CRITICAL |
| safety-req-review-verification-honesty | IEC 61508-1:2010 Cl. 7.2 | HIGH |
| safety-req-review-traceability | IEC 61508-1:2010 Cl. 7.1 | HIGH |
| safety-req-review-no-modification | IEC 62061:2021 Cl. 6 (reviewer independence) | HIGH |

## Impact tiers

| Impact tier | Meaning | Typical handling |
|---|---|---|
| CRITICAL | Safety/security-critical; release blocker; core/evidence zone | Human approval required; no autonomous AI action |
| HIGH | Major correctness or compliance impact | Reviewed change; evidence required |
| MEDIUM | Moderate impact | Standard review |
| LOW | Minor or advisory | Batched review acceptable |

### Rule impact assignments

| Rule ID | Impact tier |
|---|---|
| safety-req-review-atomicity | HIGH |
| safety-req-review-hazard-coverage | CRITICAL |
| safety-req-review-verification-honesty | HIGH |
| safety-req-review-traceability | HIGH |
| safety-req-review-no-modification | HIGH |

## Deviation management

Any deviation from a rule or standard in this skill must be recorded as a
first-class artifact (not a code comment) with all of the following:

- Rule ID
- Reason
- File / location
- Approver
- Date

Deviations against CRITICAL rules require a safety/security lead approval and
an impact assessment. Store deviation records under the project evidence or
change-control location and link them in the traceability matrix.

## Builder + reviewer pairing

This skill is the reviewer partner of `axiom-safety-requirements`. It must not modify the builder artifact; it samples evidence, records findings with severity, and emits a verdict. Independence of the reviewer is a release gate.

## Three-zone autonomy

Autonomy is zoned by risk; the V&V boundary is the automation boundary.

- Core / evidence zone (AI no access, human accountable): certified or
  qualified artifacts, evidence records, safety/security-critical code, and
  release baselines. AI must not read or write here without an explicit
  human-approved change request.
- Gray zone (AI assistant + HITL): AI plans and drafts; a human decides and
  approves each step. Architecture, requirements, tests with safety impact, and
  verification-affecting configuration live here.
- Non-critical zone (AI unrestricted): documentation, examples, scaffolding,
  low-risk refactors, and tooling glue.

This skill's outputs are treated as gray-zone by default; AI may draft but a
human approves. AI must never act autonomously in the core/evidence zone.
