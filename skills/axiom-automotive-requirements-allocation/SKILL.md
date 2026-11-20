---
name: axiom-automotive-requirements-allocation
title: Automotive requirements allocation
description: >
  Allocate automotive software requirements to architecture elements and
  components with interface contracts, ASIL-aware allocation rules and
  end-to-end traceability. Use when assigning SWE.1 software requirements to
  AUTOSAR modules, software components or ECU subsystems under Automotive
  SPICE SWE.1/SWE.2.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [automotive]
platforms: [mcu, autosar-classic, autosar-adaptive]
axiom:
  dotted_name: axiom.automotive.requirements.allocation
  domain: automotive
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [software requirement set, architecture element list, interface definitions, ASIL scope]
  outputs: [allocation map, interface contracts, unallocated-item report, traceability update]
  risk_level: medium
  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  activity: requirements-allocation
  capability_kind: domain-specific
  primary_domain: automotive
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [automotive-spice, iso-26262]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: [axiom-automotive-requirements-analysis, requirements-traceability, automotive-spice, automotive-vcycle]
---

# Automotive Requirements Allocation

## Purpose
Allocate verified software requirements (SWE.1 output) to architecture
elements -- AUTOSAR modules, software components, ECU subsystems -- with
interface contracts and traceability. Normative source is always the
approved requirement set and architecture baseline, never invented detail.

## When to Use
- A software requirement set exists and needs allocation to architecture.
- AUTOSAR module or component boundaries need requirement ownership.
- Interface contracts between allocated elements must be recorded.

## When Not to Use
- As certification or assessment proof (evidence only, assessor decides).
- Before requirements analysis is complete -- record BLOCKED, do not allocate drafts.
- For hardware allocation (route to system/HW architecture skills).

## Required Inputs
- Approved software requirement set (ids, SHALL statements, acceptance criteria).
- Architecture element list (modules, components, subsystems with owners).
- Interface definitions or interface baseline under construction.
- ASIL scope from the safety plan (or explicit non-safety declaration).

## Optional Inputs
- Prior allocation maps, change history, constraint notes.

## Prerequisites
- `axiom-automotive-requirements-analysis` output available.
- Standards registry entry confirmed for every cited standard id.

## Execution Workflow
1. Inventory inputs: requirement set revision, architecture baseline revision.
2. Allocation: assign every software requirement to exactly one owning element;
   shared requirements get one owner + explicit consumer references.
3. Interface contracts: for each cross-element requirement, record provider,
   consumer, data, timing and error-handling obligations.
4. ASIL-aware rules: allocation must respect the safety plan -- no ASIL
   requirement lands on a non-capable element without a documented safety
   measure; ASIL decomposition only per the approved safety case.
5. UNALLOCATED handling: anything unallocatable is reported with rationale
   (missing element, conflicting constraints) -- never silently dropped.
6. Traceability update: software requirement -> architecture element ->
   interface contract -> downstream design intent.
7. Change impact: re-allocation on requirement or architecture change; record
   superseded links, never rewrite history.
8. Review gate: checklist + human approval before detailed design.

## Tool Invocations
- `axiom engage --activity requirements-allocation --domain automotive` to load
  this and related skills.

## Decision Rules
- One owner per requirement; shared use is a reference, not dual ownership.
- ASIL tags come from the safety plan only; this skill never assigns ASIL.
- UNALLOCATED with rationale beats forced wrong allocation.
- Flag assumptions; require human review for safety/security output.

## Workflow
As Execution Workflow above.

## Deliverables
- Allocation map + interface contracts + unallocated-item report under
  `.axiom/runs/`.

## Acceptance Criteria
- 100% of in-scope requirements allocated or explicitly UNALLOCATED with owner.
- Every cross-element requirement has an interface contract entry.
- Traceability links resolve; checklist green.

## Acceptance
- Same gates, machine-checkable.

## Validation Procedure
- validate_skills + checklist + human gate.

## Common Failure Modes
- Dual ownership of one requirement -> enforce single owner + references.
- ASIL requirement on non-capable element -> block, escalate to safety plan.
- Missing architecture element invented -> record UNALLOCATED, request baseline update.

## Guardrails
- No secrets/shell/net; never claim compliance.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| alloc-single-owner | Automotive SPICE 4.x SWE.2 BP1 (software architectural design) | HIGH |
| alloc-interface-contracts | Automotive SPICE 4.x SWE.2 BP2 (interfaces) | HIGH |
| alloc-asil-capable-elements | ISO 26262-6:2018 Cl. 7 (software architectural design) | CRITICAL |
| alloc-unallocated-rationale | Automotive SPICE 4.x SWE.2 BP3 (traceability) | MEDIUM |
| alloc-change-impact | Automotive SPICE 4.x SWE.2 BP4 (consistency) | MEDIUM |

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
| alloc-single-owner | HIGH |
| alloc-interface-contracts | HIGH |
| alloc-asil-capable-elements | CRITICAL |
| alloc-unallocated-rationale | MEDIUM |
| alloc-change-impact | MEDIUM |

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
- Standard identifiers + landing URLs only.
