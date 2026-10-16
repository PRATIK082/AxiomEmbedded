---
name: axiom-vnv-plan
title: Verification and Validation Planning
description: >
  Use when a verification and validation plan with a requirements-to-test
  trace matrix is needed. Trigger phrases include "create a V&V plan", "plan
  verification tests", "build a traceability matrix", and "map requirements
  to tests".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.assurance.vnv_plan
  domain: industrial
  subdomain: assurance
  category: verification
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, verification, traceability]
  related_skills: [axiom-vnv-plan-review]
  lifecycle: [verification, validation]
  standards: [ISO 12100:2010, ISO 13849-2:2012, ISO/TS 15066:2016, IEC 62061:2021]
  artifact_types: [V&V plan, traceability matrix]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [safety-requirements artifact]
  outputs: [vnv-plan artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/vnv-checklist.md]
  templates: [templates/vnv-plan.template.yaml]
  scripts: [scripts/check_vnv_plan.py]
---

# Axiom Verification and Validation Planning (builder)

## Purpose
Produce a V&V plan: test cases with stable TEST-xxx IDs, covered requirements,
and a requirements-to-test trace matrix. Unexecuted tests use result not-run;
unknown results are never presented as passes.

## When to Use
- Safety requirements are baselined and verification must be planned.
- A release needs a traceability matrix for review.

## When Not to Use
- As test evidence or a pass verdict for unexecuted tests.
- As a substitute for qualified test execution.

## Required Inputs
- Safety-requirements artifact.

## Optional Inputs
- Test environment description, prior test plans.

## Prerequisites
- Requirement IDs stable.

## Execution Workflow
1. Write one or more test cases per requirement (TEST-001...).
2. Build the trace_matrix rows (requirement, test_case).
3. Set result not-run for planned tests; never invent pass/fail.
4. Fill envelope fields and open questions for missing test environments.
5. Run `scripts/check_vnv_plan.py <artifact>` plus a traceability check.
6. Submit to `axiom-vnv-plan-review`.

## Acceptance
- Validates against `schemas/assurance-vnv-plan.schema.json`.
- Every requirement appears in the trace matrix or an explicit open item.
- No test claims pass without recorded evidence.

## Assumptions and Limitations
- Plan only; execution evidence arrives later as separate artifacts.
- Environment constraints may defer tests; record deferrals openly.
- Draft evidence requiring qualified human review.
