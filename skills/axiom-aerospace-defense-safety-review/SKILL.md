---
name: axiom-aerospace-defense-safety-review
title: Aerospace and Defense Safety Review
description: >
  Reviews safety-critical embedded designs against DO-178C/DO-254-style
  objectives and evidence expectations. Use when aerospace defense safety review
  tasks arise in aerospace projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [aerospace]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.aerospace.aerospace.defense.safety.review
  domain: aerospace
  subdomain: safety
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [safety]

  related_skills: []

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [DO-178C, DO-254]
  artifact_types: [safety review]
  mcp_tools: [run_skill, validate_skill]

  risk_level: safety-critical
  review_required: true
  safety_critical: true
  inputs:
  - repository path
  - target files
  - objective
  - constraints
  outputs:
  - run report
  - run manifest
  required_tools:
  - validate_skill
  optional_tools:
  - run_skill
---
# Axiom Aerospace and Defense Safety Review

## Purpose
Reviews safety-critical embedded designs against DO-178C/DO-254-style objectives and evidence expectations.

Scope: safety (aerospace). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the aerospace and defense safety review engineering workflow.
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
- Run report under `.axiom/runs/<timestamp>/axiom-aerospace-defense-safety-review/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-aerospace-defense-safety-review`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.


## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| do178c-safety-review-objective-coverage | DO-178C Annex A (objectives by DAL) | CRITICAL |
| do178c-safety-review-evidence | DO-178C Cl. 11 (software lifecycle data) | HIGH |
| do254-safety-review-hardware | DO-254 Cl. 6 (verification) | HIGH |
| arp4754a-safety-review-system | ARP4754A Cl. 5 (development process) | HIGH |
| arp4761-safety-review-hazard | ARP4761 (safety assessment process) | CRITICAL |
| mil-std-882e-safety-review | MIL-STD-882E (system safety) | HIGH |

## Impact tiers

| Impact tier | Meaning | Typical handling |
|---|---|---|
| CRITICAL | Safety/security-critical; release blocker; core/evidence zone | Human approval required; no autonomous AI action |
| HIGH | Major correctness or compliance impact | Reviewed change; evidence required |
| MEDIUM | Moderate impact | Standard review |
| LOW | Minor or advisory | Batched review acceptable |

### Rule impact assignments

| Rule ID | Impact tier |
|---|---|
| do178c-safety-review-objective-coverage | CRITICAL |
| do178c-safety-review-evidence | HIGH |
| do254-safety-review-hardware | HIGH |
| arp4754a-safety-review-system | HIGH |
| arp4761-safety-review-hazard | CRITICAL |
| mil-std-882e-safety-review | HIGH |

## Deviation management

Any deviation from a rule or standard in this skill must be recorded as a
first-class artifact (not a code comment) with all of the following:

- Rule ID
- Reason
- File / location
- Approver
- Date

Deviations against CRITICAL rules require a safety/security lead approval and
an impact assessment. Store deviation records under the project evidence or
change-control location and link them in the traceability matrix.

## Builder + reviewer pairing

This skill is the reviewer for safety-critical aerospace and defense designs.
It must not modify the design under review; it records findings with severity
and a verdict (pass / pass-with-findings / fail). Reviewer independence is a
release gate. Solo use requires an explicit waiver recorded in the deviation
log.

## Three-zone autonomy

Autonomy is zoned by risk; the V&V boundary is the automation boundary.

- Core / evidence zone (AI no access, human accountable): certified or
  qualified artifacts, evidence records, safety/security-critical code, and
  release baselines. AI must not read or write here without an explicit
  human-approved change request.
- Gray zone (AI assistant + HITL): AI plans and drafts; a human decides and
  approves each step. Architecture, requirements, tests with safety impact, and
  verification-affecting configuration live here.
- Non-critical zone (AI unrestricted): documentation, examples, scaffolding,
  low-risk refactors, and tooling glue.

This skill's outputs are treated as gray-zone by default; AI may draft but a
human approves. AI must never act autonomously in the core/evidence zone.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
