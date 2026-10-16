---
name: axiom-v2x-communication
title: V2X Communication Design
description: >
  Models V2X messages, latency/security considerations and simulation hooks with a message test strategy.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [automotive]
platforms: [mpu]
axiom:
  dotted_name: axiom.automotive.v2x.communication
  domain: automotive
  subdomain: v2x
  category: design
  maturity: experimental
  owner: axiom-embedded
  tags: [v2x]
  related_skills: []
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [ETSI ITS-G5]
  artifact_types: [message model, test strategy]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom V2X Communication Design

## Purpose
Models V2X messages, latency/security considerations and simulation hooks with a message test strategy.

Scope: v2x (automotive). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the v2x communication design engineering workflow.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Domain artifacts for v2x (see skill references/).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing v2x artifacts.
3. Select method/template from this skill.
4. Generate or modify artifacts (dry-run first).
5. Validate structurally and semantically (scripts/ + checklists/).
6. Run applicable checks; record results.
7. Produce traceability and review evidence.
8. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer explicit configuration over invented defaults; flag every assumption.
- Safety/security-relevant outputs require human review (review_required: true).

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-v2x-communication/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-v2x-communication`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
