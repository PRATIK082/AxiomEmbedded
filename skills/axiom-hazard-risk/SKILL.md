---
name: axiom-hazard-risk
title: Hazard Analysis and Risk Assessment
description: >
  Use when a team must identify system hazards and assess risk for an embedded
  or cyber-physical product. Trigger phrases include "perform hazard analysis",
  "create a risk assessment", "identify system hazards", and "assess safety
  risks".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.assurance.hazard_risk
  domain: industrial
  subdomain: safety
  category: analysis
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, safety, hazard]

  related_skills: [axiom-hazard-risk-review]
  checklists: [checklists/hazard-checklist.md]
  templates: [templates/hazard-risk.template.yaml]
  scripts: [scripts/check_hazard_risk.py]

  lifecycle: [requirements, architecture, verification]
  standards: ["ISO 12100:2010", "ISO 10218-1:2011", "ISO 10218-2:2011", "ISO/TS 15066:2016", "ISO 13849-1:2023", "ISO 13850:2015", "ISO 14118:2017"]
  artifact_types: [hazard analysis, risk assessment]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: true
  safety_critical: true
  inputs: [system-scope artifact, incident history]
  outputs: [hazard-risk artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Hazard Analysis and Risk Assessment (builder)

## Purpose
Produce a hazard-risk artifact: identified hazards with severity, controls or
rationale, and trace links to the system scope. Every high or critical hazard
must carry at least one control or a documented rationale.

## When to Use
- After the system scope is baselined, before requirements are frozen.
- When a design change introduces new operating modes or interfaces.

## When Not to Use
- As a certification verdict or SIL/PL determination; this is draft evidence.
- When quantitative failure rates are needed; mark them OPEN unless measured.

## Required Inputs
- System-scope artifact (`kind: system-scope`).
- Operating modes and known incident or near-miss notes (may be empty but explicit).

## Optional Inputs
- Architecture sketch, prior FMEA rows, site constraints.

## Prerequisites
- Scope artifact approved or explicitly marked draft with open questions.

## Execution Workflow
1. Enumerate hazards per operating mode; assign stable IDs HAZ-001, HAZ-002, ...
2. Rate severity low/medium/high/critical with a one-line rationale each.
3. Attach controls (CTL-xxx references or text) or a rationale where no control exists.
4. Fill envelope fields including standards considered and open questions.
5. Run `scripts/check_hazard_risk.py <artifact>`; resolve errors.
6. Submit to `axiom-hazard-risk-review`; never edit the artifact after review starts.

## Acceptance
- Validates against `schemas/assurance-hazard-risk.schema.json`.
- Checker reports PASS; no high/critical hazard lacks control or rationale.
- Every hazard traces to the scope artifact.

## Assumptions and Limitations
- Severity ratings are engineering judgement, not measured risk.
- Incomplete operating modes produce incomplete hazards; record gaps as OPEN.
- This artifact supports engineering assessment and requires qualified human
  review. It is not a certification or conformity approval.






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.





## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | ISO 12100:2010 | MEDIUM |
| R2 | ISO 10218-1:2011 | MEDIUM |
| R3 | ISO 10218-2:2011 | MEDIUM |
| R4 | ISO/TS 15066:2016 | MEDIUM |
| R5 | ISO 13849-1:2023 | MEDIUM |
| R6 | ISO 13850:2015 | MEDIUM |
| R7 | ISO 14118:2017 | MEDIUM |


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

