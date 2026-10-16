---
name: axiom-hazard-risk-review
title: Hazard Analysis and Risk Assessment Review
description: >
  Use when an independent review of a hazard-risk artifact is required.
  Trigger phrases include "review hazard analysis", "audit risk assessment",
  and "check hazard coverage".
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
  lifecycle: [requirements, verification]
  standards: [ISO 12100:2010, ISO 10218-1:2011, ISO 10218-2:2011, ISO/TS 15066:2016, ISO 13849-1:2023, ISO 13850:2015, ISO 14118:2017]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: false
  safety_critical: true
  inputs: [hazard-risk artifact, system-scope artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]
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
