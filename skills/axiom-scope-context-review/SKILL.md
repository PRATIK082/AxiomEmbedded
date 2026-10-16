---
name: axiom-scope-context-review
title: System Scope and Operating Context Review
description: >
  Use when an independent review of a system-scope artifact is required.
  Trigger phrases include "review system scope", "audit operating context",
  and "check scope boundaries".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.assurance.scope_context_review
  domain: industrial
  subdomain: assurance
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, review]
  related_skills: [axiom-scope-context]
  lifecycle: [requirements]
  standards: [ISO 12100:2010, ISO 10218-2:2011, ISO 11161:2007]
  artifact_types: [review report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: false
  safety_critical: false
  inputs: [system-scope artifact]
  outputs: [review report]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/review-checklist.md]
  templates: [templates/review.template.yaml]
  scripts: [scripts/check_review.py]
---

# Axiom System Scope Review (reviewer)

## Purpose
Independently review a system-scope artifact without modifying it. Emit a
separate review report with severity-classified findings and a verdict of
accept, accept-with-actions, or revise-and-resubmit.

## Workflow
1. Read the target artifact; never edit it.
2. Copy `templates/review.template.yaml`; record target_artifact and reviewer.
3. Check boundaries, interfaces, assumptions, and open questions against
   `checklists/review-checklist.md`.
4. Classify each finding Blocker, Major, Minor, Observation, or
   Information Request, with location, evidence, recommendation, and owner.
5. Run `scripts/check_review.py <report>`; verdict revise-and-resubmit when any
   Blocker exists.

## Acceptance
- Report validates against `schemas/assurance-review.schema.json`.
- Target artifact untouched; findings carry owner and recommendation.
- Every Blocker has a recommended action.

## Limitations
- Review quality bounds to the provided artifact and inputs; field truth still
  needs qualified human confirmation. Not a conformity approval.
