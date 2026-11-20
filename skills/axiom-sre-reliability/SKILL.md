---
name: axiom-sre-reliability
title: SRE Reliability
description: >
  SRE Reliability workflow for platform. Use when sre reliability tasks arise in
  platform projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [platform]
platforms: [mcu]

axiom:
  dotted_name: axiom.platform.sre.reliability
  domain: platform
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
# Axiom SRE Reliability

## Purpose
SRE Reliability workflow for platform.

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






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.





## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | (none declared) | LOW |


## Impact tiers

| Tier | Meaning |
|---|---|
| CRITICAL | Safety/security-critical; requires human approval and impact assessment |
| HIGH | Significant impact; requires review |
| MEDIUM | Moderate impact; standard review |
| LOW | Minor impact; routine review |

### Rule impact assignments

All rules in this skill default to MEDIUM unless marked CRITICAL or HIGH
in the rule ID -> clause map above.

## Deviation management

Any deviation must be recorded with: Rule ID, reason, file/location,
approver, and date. CRITICAL-rule deviations require safety-lead approval
and an impact assessment. Deviations are first-class artifacts, not comments.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## References
- Standard identifiers + landing URLs only.
