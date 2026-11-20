---
name: axiom-aerospace-standards-applicability
title: Aerospace Standards Applicability
description: >
  Determine which aerospace standards (DO-178C, ARP4754A, DO-254, ARP4761, IEC 61508)
  govern an item and record APPLICABLE, NOT_APPLICABLE, or DEFERRED verdicts with rationale.
  Use when scoping aerospace work or assessing a standard revision against the baseline.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [aerospace]
platforms: [mcu]
axiom:
  dotted_name: axiom.aerospace.aerospace.standards.applicability
  domain: aerospace
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  risk_level: medium
  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  activity: standards-applicability
  capability_kind: domain-specific
  primary_domain: aerospace
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [do-178c, arp4754, arp4761, do-254, iec-61508]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: []
---

# Axiom Aerospace Standards Applicability

## Purpose
Determine which aerospace standards apply to a given item, version, and
contract scope -- and record the verdict with rationale. Use when scoping
aerospace work, onboarding a standard revision, or answering
which-standard-governs questions. This skill produces applicability
verdicts only. It never substitutes for the standards themselves and
never constitutes certification evidence.

## When to Use
- Use when deciding whether DO-178C, ARP4754A, DO-254, ARP4761, or
  IEC 61508 governs a component, change, or project phase.
- Use when a new revision of an applicable standard must be assessed
  against the current baseline.
- Use when a supplier, auditor, or plan asks for the applicability
  matrix of the project.

## When Not to Use
- As certification proof or Means of Compliance argument.
- To assign DAL, failure-condition severity, or safety credit --
  those come from the ARP4761 safety assessment, never from this skill.
- To reproduce normative text from licensed standards.

## Standards Baseline Rule
Every verdict cites document identifier, revision, and lifecycle state
from standards/registry.yaml. Lifecycle states: published,
draft, pre-release, proposed, withdrawn, superseded.
A draft, pre-release, or proposed document MUST NOT replace a
published baseline without an approved project decision recorded in
the applicability matrix. Withdrawn or superseded documents are
flagged, never silently carried forward.

## Applicability Verdicts
Per standard, record exactly one verdict:
- APPLICABLE -- the item falls in the standard's scope for the
  cited revision. State the scope clause reference (identifier only).
- NOT_APPLICABLE -- out of scope. State the exclusion rationale
  (e.g. non-airborne software for DO-178C, simple hardware for
  DO-254, no contractual invocation for IEC 61508).
- DEFERRED -- applicability cannot be decided yet. Record the
  blocking question, owner, and due review point. A DEFERRED
  verdict is never treated as APPLICABLE.

## Scope Guidance (identifiers only, no normative text)
- Airborne software, including model-based development artifacts
  governed by supplements: assess DO-178C applicability.
- System-level development assurance: assess ARP4754A.
- Complex custom micro-coded hardware: assess DO-254.
- Safety assessment process and DAL assignment inputs: ARP4761
  (assessment owned by the safety process, not this skill).
- IEC 61508 applies only where contractually invoked or where
  the project explicitly adopts it for non-airborne elements;
  never assume it as default for airborne items.

## DAL Rule
DAL is assigned by the ARP4761 safety assessment process and
approved in the project safety plan. This skill records the
assigned DAL as context and MUST NOT assign, upgrade, or
downgrade it.

## Inputs
- Item definition (system, hardware item, or software component).
- Contract scope and applicable standard revisions under review.
- Current applicability matrix, if one exists.

## Workflow
1. Collect the item definition and contract scope.
2. List candidate standards from the registry with revision and
   lifecycle state.
3. Assess each candidate against its scope; record APPLICABLE,
   NOT_APPLICABLE, or DEFERRED with rationale.
4. Flag withdrawn, superseded, or draft-replaces-published cases.
5. Route in-scope standards to their engineering skills
   (requirements-analysis, allocation, code-review, verification).
6. Publish the matrix and file it as review evidence.

## Outputs
- Applicability matrix (templates/applicability-matrix.md).
- Gap report listing DEFERRED verdicts with owners and dates.
- Review record passing checklists/review.yaml.

## Acceptance Criteria
- Every in-scope standard has an APPLICABLE verdict with cited
  revision and lifecycle state.
- Every NOT_APPLICABLE verdict carries an exclusion rationale.
- Every DEFERRED verdict has an owner and a review point.
- No draft document replaces a published baseline without an
  approved decision.
- No DAL assigned, upgraded, or downgraded by this skill.
- Matrix passes scripts/validate.py.

## Related Skills
- axiom-aerospace-requirements-analysis
- axiom-aerospace-requirements-allocation
- axiom-aerospace-code-review
- axiom-aerospace-verification


## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| do178c-applicability-scope | DO-178C (scope of applicability) | HIGH |
| arp4754a-applicability-system | ARP4754A (system development assurance) | HIGH |
| do254-applicability-hardware | DO-254 (hardware design assurance) | HIGH |
| arp4761-applicability-safety | ARP4761 (safety assessment process) | CRITICAL |
| iec61508-applicability-contractual | IEC 61508 (only where contractually invoked) | MEDIUM |
| standards-applicability-lifecycle-state | Standards registry lifecycle states | MEDIUM |
| standards-applicability-dal-no-assign | ARP4761 (DAL assignment ownership) | CRITICAL |

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
| do178c-applicability-scope | HIGH |
| arp4754a-applicability-system | HIGH |
| do254-applicability-hardware | HIGH |
| arp4761-applicability-safety | CRITICAL |
| iec61508-applicability-contractual | MEDIUM |
| standards-applicability-lifecycle-state | MEDIUM |
| standards-applicability-dal-no-assign | CRITICAL |

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

This skill is a builder for standards applicability verdicts. Its outputs must
be independently checked by its paired reviewer (axiom-aerospace-code-review
for artifact reviews) before acceptance. Solo use requires an explicit waiver
recorded in the deviation log.

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

