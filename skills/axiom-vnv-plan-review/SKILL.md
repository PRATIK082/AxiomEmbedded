---
name: axiom-vnv-plan-review
title: V&V Plan Review
description: >
  Use when an independent review of a V&V plan and trace matrix is required.
  Trigger phrases include "review test plan", "audit traceability matrix",
  and "check verification coverage".
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
  lifecycle: [verification, validation]
  standards: [ISO 12100:2010, ISO 13849-2:2012, ISO/TS 15066:2016, IEC 62061:2021]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: false
  safety_critical: false
  inputs: [vnv-plan artifact, safety-requirements artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]
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
