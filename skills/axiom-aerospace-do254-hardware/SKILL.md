---
name: axiom-aerospace-do254-hardware
title: DO-254 Hardware Design Assurance
description: >
  DO-254 Hardware Design Assurance workflow for aerospace. Use when do-254
  hardware design assurance tasks arise in aerospace projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [aerospace]
platforms: [mcu]

axiom:
  dotted_name: axiom.aerospace.aerospace.do254.hardware
  domain: aerospace
  maturity: experimental

  related_skills: []

  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: []
  optional_tools: []
---
# Axiom DO-254 Hardware Design Assurance

## Purpose
DO-254 Hardware Design Assurance workflow for aerospace.

## When to Use
- Concrete trigger conditions recorded per engagement.

## When Not to Use
- As certification proof.

## Required Inputs
- Repository path, target files, objective, constraints.

## Optional Inputs
- Prior reports and manifests.

## Prerequisites
- Base skills loaded.

## Execution Workflow
1. Normalize request. 2. Inspect context. 3. Select method. 4. Generate (dry-run first). 5. Validate. 6. Trace. 7. Summarize.

## Tool Invocations
- run_skill dry-run first; validate_skill gates release.

## Decision Rules
- Flag assumptions; require human review for safety/security output.

## Workflow
As Execution Workflow above.

## Deliverables
- Run report + manifest under .axiom/runs/.

## Acceptance Criteria
- Checklist green, traceability complete.

## Acceptance
- Same gates, machine-checkable.

## Validation Procedure
- validate_skills + checklist + human gate.

## Common Failure Modes
- Missing inputs invented -> require explicit inputs.

## Guardrails
- No secrets/shell/net; never claim compliance.


## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| do254-hardware-design-assurance | DO-254 Cl. 4 (design process) | HIGH |
| do254-hardware-planning | DO-254 Cl. 3 (planning process) | MEDIUM |
| do254-hardware-configuration | DO-254 Cl. 7 (configuration management) | MEDIUM |
| do254-hardware-verification | DO-254 Cl. 6 (verification process) | HIGH |
| do254-hardware-complex-hardware | DO-254 (complex hardware identification) | HIGH |
| do254-hardware-evidence | DO-254 (hardware lifecycle data) | HIGH |

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
| do254-hardware-design-assurance | HIGH |
| do254-hardware-planning | MEDIUM |
| do254-hardware-configuration | MEDIUM |
| do254-hardware-verification | HIGH |
| do254-hardware-complex-hardware | HIGH |
| do254-hardware-evidence | HIGH |

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

This skill is a builder for DO-254 hardware design assurance. Its outputs must
be independently checked by a qualified reviewer (axiom-aerospace-code-review
for artifact reviews, plus a human reviewer for certification evidence) before
acceptance. Solo use requires an explicit waiver recorded in the deviation
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
- Standard identifiers + landing URLs only.
