---
name: axiom-multi-agent-orchestration
title: Multi-Agent Orchestration
description: >
  Multi-Agent Orchestration workflow for platform. Use when multi-agent
  orchestration tasks arise in platform projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [platform]
platforms: [mcu]

axiom:
  dotted_name: axiom.platform.multi.agent.orchestration
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
# Axiom Multi-Agent Orchestration

## Purpose
Multi-Agent Orchestration workflow for platform.

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


## Deviation management

Any deviation from a rule or standard must be recorded with: Rule ID, reason,
file/location, approver, and date. Deviations are tracked as first-class
artifacts, not comments. (Straion pattern.)


## Builder + reviewer

This skill follows the builder + reviewer pattern: the builder produces the
artifact, the reviewer independently verifies it before acceptance. No
artifact is accepted without reviewer sign-off.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## Copyright-safe standards

Never reproduce normative standards text. Store identifiers, clause numbers,
applicability metadata, mappings, and project-authored interpretations only.


## References
- Standard identifiers + landing URLs only.
