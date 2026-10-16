---
name: axiom-safety-requirements-review
title: Safety Requirements Review
description: >
  Use when an independent review of safety requirements is required. Trigger
  phrases include "review safety requirements", "audit requirement coverage",
  and "check requirements traceability".
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
  lifecycle: [requirements]
  standards: [ISO 12100:2010, ISO 13849-1:2023, ISO 13850:2015, ISO 14118:2017, IEC 62061:2021, IEC 61508:2010]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: false
  safety_critical: true
  inputs: [safety-requirements artifact, hazard-risk artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]
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
