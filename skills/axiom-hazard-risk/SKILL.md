---
name: axiom-hazard-risk
title: Hazard Analysis and Risk Assessment
description: >
  Use when a team must identify system hazards and assess risk for an
  embedded or cyber-physical product. Trigger phrases include "perform hazard
  analysis", "create a risk assessment", "identify system hazards", and
  "assess safety risks".
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
  maturity: beta
  owner: axiom-embedded
  tags: [assurance, safety, hazard]
  related_skills: [axiom-hazard-risk-review]
  lifecycle: [requirements, architecture, verification]
  standards: [ISO 12100:2010, ISO 10218-1:2011, ISO 10218-2:2011, ISO/TS 15066:2016, ISO 13849-1:2023, ISO 13850:2015, ISO 14118:2017]
  artifact_types: [hazard analysis, risk assessment]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: true
  safety_critical: true
  inputs: [system-scope artifact, incident history]
  outputs: [hazard-risk artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/hazard-checklist.md]
  templates: [templates/hazard-risk.template.yaml]
  scripts: [scripts/check_hazard_risk.py]
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
