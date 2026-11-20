---
name: axiom-safety-requirements
title: Safety Requirements Derivation
description: >
  Use when safety requirements must be derived from hazards and scope for an
  embedded product. Trigger phrases include "derive safety requirements", "write
  safety goals", "map hazards to requirements", and "safety requirements
  specification".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.assurance.safety_requirements
  domain: industrial
  subdomain: safety
  category: requirements
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, safety, requirements]

  related_skills: [axiom-safety-requirements-review]
  checklists: [checklists/requirements-checklist.md]
  templates: [templates/safety-requirements.template.yaml]
  scripts: [scripts/check_safety_requirements.py]

  lifecycle: [requirements, architecture]
  standards: ["ISO 12100:2010", "ISO 13849-1:2023", "ISO 13850:2015", "ISO 14118:2017", "IEC 62061:2021", "IEC 61508:2010"]
  artifact_types: [safety requirements]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: true
  safety_critical: true
  inputs: [hazard-risk artifact, system-scope artifact]
  outputs: [safety-requirements artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Safety Requirements Derivation (builder)

## Purpose
Derive verifiable safety requirements from hazards, each with a stable REQ-xxx
ID, covered hazards, and a verification method (test, inspection, analysis,
or explicit OPEN).

## When to Use
- Hazard analysis exists and requirements must be written before design freeze.
- A hazard gains a new control that needs a requirement owner.

## When Not to Use
- As proof that requirements are complete or sufficient for certification.
- To invent supplier capabilities or test results.

## Required Inputs
- Hazard-risk artifact and system-scope artifact.

## Optional Inputs
- Architecture concept, prior requirement sets.

## Prerequisites
- Hazard IDs stable; scope boundaries agreed or marked draft.

## Execution Workflow
1. For each hazard control, write one or more atomic requirements (REQ-001...).
2. Set covers_hazards, verification method, and status per requirement.
3. Requirements without a known verification method use verification OPEN
   plus an open question naming the owner.
4. Fill envelope fields and traceability links back to HAZ-xxx IDs.
5. Run `scripts/check_safety_requirements.py <artifact>`; fix errors.
6. Submit to `axiom-safety-requirements-review`.

## Acceptance
- Validates against `schemas/assurance-safety-requirements.schema.json`.
- Every high/critical hazard is covered by at least one requirement or a
  documented rationale.
- No requirement text contains TBD without a matching open question.

## Assumptions and Limitations
- Coverage is claimed against known hazards only; unknown hazards are out of scope.
- Verification methods are planned, not executed, at this stage.
- Draft evidence requiring qualified human review; not a conformity approval.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| safety-req-atomicity | IEC 62061:2021 Cl. 6 (safety requirements specification) | HIGH |
| safety-req-verifiability | IEC 61508-1:2010 Cl. 7.2 (safety requirements) | HIGH |
| safety-req-hazard-coverage | ISO 12100:2010 Cl. 6 (risk assessment) | CRITICAL |
| safety-req-verification-method | ISO 13849-1:2023 Cl. 7 (validation) | HIGH |
| safety-req-traceability | IEC 61508-1:2010 Cl. 7.1 | HIGH |
| safety-req-no-tbd-without-owner | IEC 62061:2021 Cl. 6 | MEDIUM |

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
| safety-req-atomicity | HIGH |
| safety-req-verifiability | HIGH |
| safety-req-hazard-coverage | CRITICAL |
| safety-req-verification-method | HIGH |
| safety-req-traceability | HIGH |
| safety-req-no-tbd-without-owner | MEDIUM |

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

This skill is a builder. Its output must be independently checked by its paired reviewer before acceptance: `axiom-safety-requirements-review`. Reviewers do not modify the artifact; they record a verdict (pass / pass-with-findings / fail). Solo use requires an explicit waiver recorded in the deviation log.

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
