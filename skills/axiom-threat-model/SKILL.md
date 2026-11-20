---
name: axiom-threat-model
title: Cybersecurity Threat Modeling
description: >
  Use when a cybersecurity threat model with risk-ranked threats and controls is
  needed for a connected embedded product. Trigger phrases include "create a
  threat model", "assess cybersecurity risks", "model attack surfaces", and
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
  maturity: experimental
  owner: axiom-embedded
  tags: [assurance, cybersecurity, threat]

  related_skills: [axiom-threat-model-review]
  checklists: [checklists/threat-checklist.md]
  templates: [templates/threat-model.template.yaml]
  scripts: [scripts/check_threat_model.py]

  lifecycle: [requirements, architecture, verification]
  standards: ["IEC 62443-3-3:2013", "IEC 62443-3-2:2020", "IEC 62443-4-1:2018", "IEC 62443-4-2:2019"]
  artifact_types: [threat model]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: true
  safety_critical: false
  inputs: [system-scope artifact, architecture sketch]
  outputs: [threat-model artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
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

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| threat-sec-attack-surface-coverage | IEC 62443-3-2:2020 Cl. 6 (risk assessment) | CRITICAL |
| threat-sec-severity-rating | IEC 62443-3-3:2013 Cl. 7 (risk treatment) | MEDIUM |
| threat-sec-control-attachment | IEC 62443-4-1:2018 Cl. 8 (secure design) | HIGH |
| threat-sec-verification-reference | IEC 62443-4-1:2018 Cl. 9 (verification) | HIGH |
| threat-sec-no-unimplemented-control-claims | IEC 62443-4-2:2019 (component requirements) | HIGH |

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
| threat-sec-attack-surface-coverage | CRITICAL |
| threat-sec-severity-rating | MEDIUM |
| threat-sec-control-attachment | HIGH |
| threat-sec-verification-reference | HIGH |
| threat-sec-no-unimplemented-control-claims | HIGH |

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

This skill is a builder. Its output must be independently checked by its paired reviewer before acceptance: `axiom-threat-model-review`. Reviewers do not modify the artifact; they record a verdict (pass / pass-with-findings / fail). Solo use requires an explicit waiver recorded in the deviation log.

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
