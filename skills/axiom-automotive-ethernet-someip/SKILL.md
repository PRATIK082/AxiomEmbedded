---
name: axiom-automotive-ethernet-someip
title: Automotive Ethernet and SOME/IP Design
description: >
  Designs Ethernet topology, VLAN/TSN assumptions and SOME/IP service modeling
  for service-oriented ECUs. Use when automotive ethernet someip tasks arise in
  automotive projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [automotive]
platforms: [mpu, autosar-adaptive]

axiom:
  dotted_name: axiom.automotive.automotive.ethernet.someip
  domain: automotive
  subdomain: networks
  category: design
  maturity: experimental
  owner: axiom-embedded
  tags: [networks]

  related_skills: []

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [AUTOSAR SOME/IP, IEEE 802.1 TSN]
  artifact_types: [Ethernet design, service model]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
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
# Axiom Automotive Ethernet and SOME/IP Design

## Purpose
Designs Ethernet topology, VLAN/TSN assumptions and SOME/IP service modeling for service-oriented ECUs.

Scope: networks (automotive). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the automotive ethernet and some/ip design engineering workflow.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Domain artifacts for networks (see skill references/).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing networks artifacts.
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
- Run report under `.axiom/runs/<timestamp>/axiom-automotive-ethernet-someip/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-automotive-ethernet-someip`.
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
| eth-topology-vlan-tsn | IEEE 802.1Q-2022 Cl. 8 (VLANs and traffic classes) | MEDIUM |
| eth-tsn-gating | IEEE 802.1Qbv Cl. 8 (time-aware shaper) | HIGH |
| someip-service-model | AUTOSAR PRS_SOMEIP (service-oriented communication) | MEDIUM |
| someip-sd-ttl | AUTOSAR PRS_SOMEIPSD (service discovery) | MEDIUM |
| eth-qos-priority | IEEE 802.1Q-2022 Cl. 6 (priority and traffic classes) | MEDIUM |

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
| eth-topology-vlan-tsn | MEDIUM |
| eth-tsn-gating | HIGH |
| someip-service-model | MEDIUM |
| someip-sd-ttl | MEDIUM |
| eth-qos-priority | MEDIUM |

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

Where this skill produces an artifact, pair it with an independent confirmation
review before acceptance; reviewers do not modify the artifact. No dedicated reviewer skill is assigned in the catalog for this skill; use the domain review skill or a human reviewer.

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
