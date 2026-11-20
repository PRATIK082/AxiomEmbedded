---
name: axiom-automotive-requirements-analysis
title: Automotive requirements analysis
description: >
  Analyze automotive stakeholder and system inputs into verifiable software
  requirements with allocation, ASIL-aware tagging and traceability hooks.
  Use when decomposing ECU, AUTOSAR or vehicle functions into SHALL-level
  software requirements under Automotive SPICE SWE.1.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [automotive]
platforms: [mcu, autosar-classic, autosar-adaptive]
axiom:
  dotted_name: axiom.automotive.requirements.analysis
  domain: automotive
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [stakeholder needs, system requirements, operating scenarios, constraints, ASIL scope]
  outputs: [software requirement set, allocation map, acceptance criteria, gap report]
  risk_level: medium
  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  activity: requirements-analysis
  capability_kind: domain-specific
  primary_domain: automotive
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [automotive-spice, iso-26262]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: [requirements, requirements-traceability, automotive-spice, automotive-vcycle]
---

# Automotive Requirements Analysis

## Purpose
Decompose automotive stakeholder needs and system requirements into atomic,
verifiable software requirements (SWE.1), with allocation, acceptance criteria
and end-to-end traceability hooks. Normative source is always the supplied
OEM/AUTOSAR/ASPICE baseline -- never invented detail.

## When to Use
- New ECU, AUTOSAR module or vehicle function needs a software requirement set.
- Stakeholder/system requirements exist and need SWE.1 decomposition.
- Gap analysis between project scope and applicable standards is required.

## When Not to Use
- As certification or assessment proof (evidence only, assessor decides).
- For hardware-only or pure-calibration requirements (route to HW/calibration skills).
- When no source baseline exists -- record BLOCKED, do not invent requirements.

## Required Inputs
- Source baseline: stakeholder requirements, system requirements, applicable
  standards edition (ASPICE version, ISO 26262 part if in safety scope).
- Operating scenarios, constraints, interfaces, ASIL scope (or explicit
  non-safety declaration).

## Optional Inputs
- Prior architecture sketches, existing requirement databases, change history.

## Prerequisites
- `requirements` (generic elicitation) loaded for method baseline.
- Standards registry entry confirmed for every cited standard id.

## Execution Workflow
1. Inventory sources: id, revision, hash/page for every input document.
2. Extract stakeholder needs; tag each with source reference.
3. Derive software requirements: one verifiable statement per requirement,
   SHALL-form, with acceptance criteria and verification method (test,
   analysis, inspection).
4. Allocate each software requirement to architecture elements (or record
   UNALLOCATED with rationale).
5. Tag safety relevance: ASIL from the safety plan, or explicit NON-SAFETY.
6. Build traceability stubs: stakeholder -> system -> software -> test intent.
7. Gap report: uncovered inputs, conflicts, UNRESOLVED items with owners.
8. Review gate: checklist + human approval before downstream design.

## Tool Invocations
- `axiom engage --activity requirements-analysis --domain automotive` to load
  this and related skills.
- `validate_skill` gates release; checklists/review.yaml gates human review.

## Decision Rules
- Every requirement carries a source reference; unsourced text is a gap, not
  a requirement.
- Conflicts between sources escalate to the owner; never silently resolve.
- ASIL tags come from the safety plan only; never assign ASIL here.

## Deliverables
- Software requirement set (id, statement, source, acceptance, verification).
- Allocation map + gap report under `.axiom/runs/`.

## Acceptance Criteria
- 100% of in-scope inputs mapped or explicitly waived with rationale.
- Every software requirement has acceptance criteria + verification method.
- Traceability stubs complete to test intent.

## Acceptance
- Checklist green, pipeline `--check` green, human review APPROVED.

## Validation Procedure
- `validate_skill` + checklist + `skill_pipeline.py --check` + reviewer sign-off.

## Common Failure Modes
- Invented requirements without source -> reject; mark UNRESOLVED.
- Unverifiable adjectives ("fast", "robust") -> rewrite with measures.
- Missing ASIL scope -> BLOCKED until safety plan input arrives.

## Guardrails
- No normative standard text reproduced; identifiers and references only.
- Never claim ASPICE capability or ASIL compliance from this analysis.


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


## References
- Automotive SPICE 4.x SWE.1 (identifier only; see standards/registry.yaml).
- ISO 26262 software safety requirements (safety scope only).
