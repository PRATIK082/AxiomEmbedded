---
name: axiom-scope-context
title: System Scope and Operating Context Definition
description: >
  Use when an engineering team must define system scope, operating context,
  and boundaries for an embedded or cyber-physical product. Trigger phrases
  include "define system scope", "capture operating context", "set system
  boundaries", and "scope the robot cell".
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [industrial, robotics]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.assurance.scope_context
  domain: industrial
  subdomain: assurance
  category: requirements
  maturity: beta
  owner: axiom-embedded
  tags: [assurance, scope]
  related_skills: [axiom-scope-context-review]
  lifecycle: [requirements, architecture]
  standards: [ISO 12100:2010, ISO 10218-2:2011, ISO 11161:2007]
  artifact_types: [system scope]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [stakeholder notes, site survey, interface list]
  outputs: [system-scope artifact]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists: [checklists/scope-checklist.md]
  templates: [templates/scope.template.yaml]
  scripts: [scripts/check_scope.py]
---

# Axiom System Scope and Operating Context (builder)

## Purpose
Produce a bounded system-scope artifact: what the system is, where it operates,
who interacts with it, and what is explicitly out of scope. Downstream hazard,
requirements, V&V, and threat work depend on this boundary.

## When to Use
- A new product, cell, or feature needs an agreed scope baseline.
- Scope drift or unclear interfaces are causing rework.

## When Not to Use
- As a safety certificate or compliance proof; this is draft engineering evidence.
- When field measurements are required; record them as OPEN instead of inventing.

## Required Inputs
- `scope-inputs.yaml`: system name, purpose, environment, operators, interfaces.

## Optional Inputs
- Site layout, prior scope documents, stakeholder list.

## Prerequisites
- Access to stakeholders who can confirm boundaries.

## Execution Workflow
1. Ingest `scope-inputs.yaml`; mark every unknown as UNKNOWN or OPEN.
2. Copy `templates/scope.template.yaml`; fill system, operating_context, boundaries.
3. Add envelope fields: artifact_id, schema_version, timestamps (UTC ISO 8601),
   author, status, domain, standards, assumptions, evidence, traceability,
   open_questions, approval_status.
4. Run `scripts/check_scope.py <artifact>`; resolve every error.
5. Hand the artifact to `axiom-scope-context-review`; never self-approve.

## Acceptance
- Artifact validates against `schemas/assurance-scope.schema.json`.
- Checker script reports PASS.
- In-scope and out-of-scope lists are both non-empty.
- At least one open question or assumption is recorded where input was incomplete.

## Assumptions and Limitations
- Assumes stakeholder inputs are current; does not verify site conditions.
- Cannot detect undeclared interfaces; review must challenge completeness.
- This artifact supports engineering assessment only and requires qualified
  human review. Formal conformity depends on the applicable regulatory scheme
  and authorized assessment.
