---
name: axiom-safety-requirements
title: Safety Requirements Derivation
description: >
  Use when safety requirements must be derived from hazards and scope for an
  embedded product. Trigger phrases include "derive safety requirements",
  "write safety goals", "map hazards to requirements", and "safety
  requirements specification".
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
  lifecycle: [requirements, architecture]
  standards: [ISO 12100:2010, ISO 13849-1:2023, ISO 13850:2015, ISO 14118:2017, IEC 62061:2021, IEC 61508:2010]
  artifact_types: [safety requirements]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: true
  safety_critical: true
  inputs: [hazard-risk artifact, system-scope artifact]
  outputs: [safety-requirements artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/requirements-checklist.md]
  templates: [templates/safety-requirements.template.yaml]
  scripts: [scripts/check_safety_requirements.py]
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
