---
name: axiom-threat-model
title: Cybersecurity Threat Modeling
description: >
  Use when a cybersecurity threat model with risk-ranked threats and controls
  is needed for a connected embedded product. Trigger phrases include "create
  a threat model", "assess cybersecurity risks", "model attack surfaces", and
  "define security controls".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.assurance.threat_model
  domain: industrial
  subdomain: cybersecurity
  category: analysis
  maturity: beta
  owner: axiom-embedded
  tags: [assurance, cybersecurity, threat]
  related_skills: [axiom-threat-model-review]
  lifecycle: [requirements, architecture, verification]
  standards: [IEC 62443-3-3:2013, IEC 62443-3-2:2020, IEC 62443-4-1:2018, IEC 62443-4-2:2019]
  artifact_types: [threat model]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: true
  safety_critical: false
  inputs: [system-scope artifact, architecture sketch]
  outputs: [threat-model artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/threat-checklist.md]
  templates: [templates/threat-model.template.yaml]
  scripts: [scripts/check_threat_model.py]
---

# Axiom Cybersecurity Threat Modeling (builder)

## Purpose
Produce a threat-model artifact: attack-surface threats with SEC-xxx IDs,
severity, controls, and verification references. Threats without known
controls stay explicit with an owner and open question.

## When to Use
- A connected device, cell controller, or gateway handles untrusted input.
- A release needs a security review baseline.

## When Not to Use
- As a security certification or penetration-test report.
- To assert controls that are not implemented or verified.

## Required Inputs
- System-scope artifact; list of external interfaces and trust boundaries.

## Optional Inputs
- Architecture sketch, asset inventory, prior incidents.

## Prerequisites
- Scope interfaces enumerated; unknown interfaces marked OPEN.

## Execution Workflow
1. Enumerate threats per trust boundary (SEC-001...).
2. Rate severity; attach controls (CTL-xxx or text) and verification references.
3. Threats without controls get an owner and open question, never silence.
4. Fill envelope fields including standards considered.
5. Run `scripts/check_threat_model.py <artifact>`; fix errors.
6. Submit to `axiom-threat-model-review`.

## Acceptance
- Validates against `schemas/assurance-threat-model.schema.json`.
- Every external interface has at least one mapped threat or a rationale.
- No control claims a verification result without evidence.

## Assumptions and Limitations
- Model covers known interfaces; covert channels and supply-chain depth are
  limited to declared inputs.
- Severity is judgement pending testing.
- Draft evidence requiring qualified human review; not a security certificate.
