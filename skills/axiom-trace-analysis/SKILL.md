---
name: axiom-trace-analysis
title: Trace Analysis
description: >
  Analyzes execution traces for timing, dropped events and anomaly triage with a deterministic parser script.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.trace.analysis
  domain: platform
  subdomain: observability
  category: verification
  maturity: experimental
  owner: axiom-embedded
  tags: [observability]
  related_skills: []
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [trace analysis report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: low
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom Trace Analysis

## Purpose
Analyzes execution traces for timing, dropped events and anomaly triage with a deterministic parser script.

Scope: observability (platform). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the trace analysis engineering workflow.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Domain artifacts for observability (see skill references/).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing observability artifacts.
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
- Run report under `.axiom/runs/<timestamp>/axiom-trace-analysis/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-trace-analysis`.
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
