---
name: axiom-aerospace-requirements-allocation
title: Aerospace requirements allocation
description: >
  Aerospace requirements allocation workflow for aerospace. Use when aerospace requirements allocation tasks arise in aerospace projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [aerospace]
platforms: [mcu]
axiom:
  dotted_name: axiom.aerospace.aerospace.requirements.allocation
  domain: aerospace
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  risk_level: medium
  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  activity: requirements-allocation
  capability_kind: domain-specific
  primary_domain: aerospace
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [arp4754, do-178c]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: []
---

# Axiom Aerospace requirements allocation

## Purpose
Allocate aerospace system requirements to software, hardware, and LRU items with single-owner accountability, per ARP4754A allocation principles and DO-178C HLR allocation. Every system requirement ends ALLOCATED (with owner + interface contract) or UNALLOCATED (with written rationale) - no silent drops.

## When to Use
- Allocating ARP4754A system requirements to software vs hardware vs LRU items.
- Deriving software HLRs from allocated system requirements for DO-178C compliance.
- Recording allocation decisions with traceability for certification audits.
- Re-allocating after design changes or derived-requirement discovery.

## When Not to Use
- As certification proof or a substitute for applicant/CB review.
- For DAL assignment without the ARP4761 safety assessment as input.

## Required Inputs
- System requirements baseline (from axiom-aerospace-requirements-analysis).
- System architecture: LRUs, hardware items, software items, interfaces.
- ARP4761 safety assessment outputs (FHA/PSSA) for DAL-related allocation constraints.
- DO-178C software level (A-E) targets per software item, where assigned.

## Workflow
1. Collect the system requirements baseline with IDs and source references.
2. For each requirement, decide: software / hardware / LRU-level / shared allocation.
3. Assign exactly one owner per allocated requirement; record interface contracts at allocation boundaries.
4. Flag derived requirements discovered during allocation; feed them back to the analysis baseline.
5. Constrain DAL-relevant allocation by the ARP4761 safety assessment; never invent DAL in this skill.
6. Mark requirements that cannot be allocated UNALLOCATED with rationale and change impact.
7. Verify allocation completeness: every system requirement accounted for exactly once.
8. Record the allocation matrix and change history for audit.

## Allocation Rules
- One requirement, one owner. Shared ownership is recorded as joint with a named primary.
- Allocation across an interface always creates an interface contract both sides reference.
- Safety-related allocation follows the safety assessment; DAL comes from ARP4761, never from engineering judgment in this skill.
- UNALLOCATED is a verdict, not an omission: it requires rationale, risk note, and approval pointer.
- Re-allocation after design change re-runs completeness verification; stale allocations are BLOCKED, not carried forward silently.

## Verification Hooks
- Completeness: count(ALLOCATED) + count(UNALLOCATED) == count(system requirements).
- Every ALLOCATED row references an existing architecture item and owner.
- Every UNALLOCATED row carries rationale + risk + approval pointer.
- Derived requirements flagged during allocation appear in the analysis baseline.
- Interface contracts exist for every cross-item allocation.

## Evidence Outputs
- Allocation matrix (system requirement -> item, owner, contract, status).
- UNALLOCATED rationale register.
- Derived-requirement feedback list.
- Completeness verification record with counts.

## Related Skills
- axiom-aerospace-requirements-analysis (source baseline)
- axiom-aerospace-requirements-verification (closure of allocated requirements)
- axiom-aerospace-standards-applicability (standard applicability verdicts)
- axiom-aerospace-code-review (review of allocation records)

## Failure Modes
- Orphan requirement: in baseline, in no allocation row. Treat as BLOCKED.
- Dual ownership without a named primary. Treat as BLOCKED.
- Cross-item allocation without an interface contract. Treat as BLOCKED.
- DAL asserted from allocation judgment rather than ARP4761. Reject the DAL claim.

## Acceptance Criteria
- Allocation matrix covers 100 percent of the system baseline (ALLOCATED or UNALLOCATED).
- Every ALLOCATED row names one owner and one architecture item.
- Every UNALLOCATED row carries rationale, risk, and approval pointer.
- Completeness counts reconcile exactly; the verification record is signed.


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

