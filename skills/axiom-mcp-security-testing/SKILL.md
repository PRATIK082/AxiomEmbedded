---
name: axiom-mcp-security-testing
title: MCP Security Testing
description: >
  MCP Security Testing workflow for all. Use when mcp security testing tasks
  arise in all projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [all]
platforms: [mcu]

axiom:
  dotted_name: axiom.all.mcp.security.testing
  domain: all
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
# Axiom MCP Security Testing

## Purpose
MCP Security Testing workflow for all.

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

## References
- Standard identifiers + landing URLs only.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| mcp-security-authz | Project rule (no external standard cited) | HIGH |
| mcp-security-input-validation | Project rule (no external standard cited) | HIGH |
| mcp-security-secret-scanning | Project rule (no external standard cited) | CRITICAL |
| mcp-security-tool-permissions | Project rule (no external standard cited) | HIGH |

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
| mcp-security-authz | HIGH |
| mcp-security-input-validation | HIGH |
| mcp-security-secret-scanning | CRITICAL |
| mcp-security-tool-permissions | HIGH |

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

Where this skill produces an artifact, pair it with an independent confirmation review before acceptance; reviewers do not modify the artifact. No single dedicated reviewer skill is assigned in the catalog for this legacy skill, so use the domain review skill or a human reviewer.

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
