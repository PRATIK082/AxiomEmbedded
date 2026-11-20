---
name: axiom-threat-model-review
title: Threat Model Review
description: >
  Use when an independent review of a cybersecurity threat model is required.
  Trigger phrases include "review threat model", "audit security controls", and
  "check attack surface coverage".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.assurance.threat_model_review
  domain: industrial
  subdomain: cybersecurity
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, review, cybersecurity]

  related_skills: [axiom-threat-model]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]

  lifecycle: [requirements, verification]
  standards: ["IEC 62443-3-3:2013", "IEC 62443-3-2:2020", "IEC 62443-4-1:2018", "IEC 62443-4-2:2019"]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: false
  safety_critical: false
  inputs: [threat-model artifact, system-scope artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Threat-Model Review (reviewer)

## Purpose
Independently review the threat model for interface coverage and control
honesty without modifying the source artifact.

## Workflow
1. Read target and scope artifacts; never edit them.
2. Verify every external interface maps to a threat or rationale.
3. Flag asserted-but-unimplemented controls and missing trust boundaries.
4. Classify findings; run the review checker.

## Acceptance
- Validates against `schemas/assurance-review.schema.json`.
- Uncovered external interfaces are Blockers; unevidenced controls are Major
  or Blocker.
- Draft evidence; not a security certificate. Qualified human review required.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| threat-sec-review-interface-coverage | IEC 62443-3-2:2020 Cl. 6 | CRITICAL |
| threat-sec-review-control-honesty | IEC 62443-4-1:2018 Cl. 8-9 | HIGH |
| threat-sec-review-trust-boundaries | IEC 62443-3-3:2013 Cl. 7 | HIGH |
| threat-sec-review-no-modification | IEC 62443-4-2:2019 (reviewer independence) | HIGH |

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
| threat-sec-review-interface-coverage | CRITICAL |
| threat-sec-review-control-honesty | HIGH |
| threat-sec-review-trust-boundaries | HIGH |
| threat-sec-review-no-modification | HIGH |

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

This skill is the reviewer partner of `axiom-threat-model`. It must not modify the builder artifact; it samples evidence, records findings with severity, and emits a verdict. Independence of the reviewer is a release gate.

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
