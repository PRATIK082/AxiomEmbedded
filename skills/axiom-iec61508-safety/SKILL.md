---
name: axiom-iec61508-safety
title: IEC 61508 Safety Lifecycle
description: >
  Supports IEC 61508 safety lifecycle, SIL determination and evidence.
version: 0.1.0
author: PRATIK PATIL
license: Apache-2.0
domains: [industrial]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.industrial.iec61508.safety
  domain: industrial
  subdomain: safety
  category: safety
  maturity: experimental
  owner: axiom-embedded
  tags: [safety]
  related_skills: []
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [IEC 61508]
  artifact_types: [safety plan, SIL allocation]
  mcp_tools: [run_skill, validate_skill]
  risk_level: safety-critical
  review_required: true
  safety_critical: true
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom IEC 61508 Safety Lifecycle

## Purpose
Supports IEC 61508 safety lifecycle, SIL determination and evidence.

Scope: safety (industrial). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the iec 61508 safety lifecycle engineering workflow.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Domain artifacts for safety (see skill references/).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing safety artifacts.
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
- Run report under `.axiom/runs/<timestamp>/axiom-iec61508-safety/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-iec61508-safety`.
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
