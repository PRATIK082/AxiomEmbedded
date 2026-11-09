---
name: axiom-medical-iec62304-lifecycle
title: IEC 62304 Medical Software Lifecycle
description: 'IEC 62304 Medical Software Lifecycle workflow for industrial. Use when
  iec 62304 medical software lifecycle tasks arise in industrial projects.

  '
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains:
- industrial
platforms:
- mcu
axiom:
  dotted_name: axiom.industrial.medical.iec62304.lifecycle
  domain: industrial
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs:
  - repository path
  - objective
  - constraints
  outputs:
  - run report
  - run manifest
  risk_level: medium
  lifecycle:
  - discover
  - plan
  - implement
  - verify
  - evidence
  artifact_types:
  - report
  - manifest
  related_skills: []
  standards: []
  mcp_tools: []
---

# Axiom IEC 62304 Medical Software Lifecycle

## Purpose
IEC 62304 Medical Software Lifecycle workflow for industrial.

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
