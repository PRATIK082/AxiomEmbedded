---
name: axiom-threat-model-review
title: Threat Model Review
description: >
  Use when an independent review of a cybersecurity threat model is required.
  Trigger phrases include "review threat model", "audit security controls",
  and "check attack surface coverage".
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
  maturity: beta
  owner: axiom-embedded
  tags: [assurance, review, cybersecurity]
  related_skills: [axiom-threat-model]
  lifecycle: [requirements, verification]
  standards: [IEC 62443-3-3:2013, IEC 62443-3-2:2020, IEC 62443-4-1:2018, IEC 62443-4-2:2019]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: false
  safety_critical: false
  inputs: [threat-model artifact, system-scope artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]
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
