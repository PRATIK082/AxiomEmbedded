---
name: axiom-aerospace-code-review
title: Aerospace Code Review
description: >
  Aerospace Code Review workflow for aerospace. Use when aerospace code review tasks arise in aerospace projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [aerospace]
platforms: [mcu]
axiom:
  dotted_name: axiom.aerospace.aerospace.code.review
  domain: aerospace
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  risk_level: medium
  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  activity: code-review
  capability_kind: domain-specific
  primary_domain: aerospace
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [do-178c, arp4754]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: []
---


# Aerospace Code Review

Use this skill when reviewing aerospace software artifacts (requirements,
design, source code) for correctness, standard compliance, and verification
credit under DO-178C and ARP4754A.

## Scope

This skill covers the process-level review workflow: review planning,
checklist-driven examination, independence management, finding disposition,
and review records that serve as DO-178C verification evidence (reviews and
analyses per DO-178C section 6.3). It does NOT replace technique-level
checks (static analysis, coverage, unit testing); delegate those to the
referenced skills and record their reports as review inputs.

## Standards basis

- ARP4754A: system-level reviews (PDR, CDR) that bound software reviews.
- DO-178C section 6: verification process objectives; reviews provide
  verification credit for requirements, design, and code objectives.
- DO-178C section 11: review records are required verification evidence.
- DAL-specific objective satisfaction per DO-178C Annex A tables.
- Lifecycle gate: draft material must never replace a published standard.

## Review planning

1. Identify the artifact under review and its type: HLR, LLR, source code,
   verification case/procedure, or verification result.
2. Select the checklist for the artifact type from checklists/review.yaml.
3. Assign reviewers meeting the independence required for the item DAL:
   - DAL A/B: verification independence required (reviewer particulier
     from the author). Record reviewer identity and independence basis.
   - DAL C and below: independence recommended; record any exception.
4. Define entry criteria: artifact complete, prior review findings closed,
   parent requirements approved, tools qualified where credit is claimed.

## Review execution

1. Trace each review unit (requirement, design element, code unit) to its
   parent: HLR to system requirements, LLR to HLR, code to LLR/design.
   Flag UNTRACTED items as findings; never waive traceability silently.
2. Examine the artifact against every gate in checklists/review.yaml.
3. Check requirement quality for HLR/LLR: unambiguous, verifiable,
   consistent, complete, traceable (DO-178C HLR characteristics).
4. Check code against: compliance with LLR/design, no dead code (DAL A/B
   dead-code justification required), no deactivated code without
   rationale, data/coupling analysis coverage, standards compliance.
5. Check verification artifacts: cases cover normal and robustness cases,
   procedures executable, results match expected outcomes, coverage
   analysis complete for the DAL.
6. Classify each finding: DEFECT (must fix), QUERY (author clarification),
   OBSERVATION (process improvement, non-blocking). Never downgrade a
   DEFECT to OBSERVATION to meet schedule.

## Requirements-archaeology rule

DAL assignment comes ONLY from the ARP4761 safety assessment. A review
never assigns, raises, or lowers a DAL. If the artifact implies a DAL
change, raise a QUERY to the safety process and BLOCK the review verdict
until resolved.

## Verdict contract

Record verdicts per review unit using templates/review-record.md:

- PASS: all gates satisfied, no open DEFECT findings.
- CONDITIONAL PASS: minor QUERY items only, with owners and due dates.
- FAIL: one or more open DEFECT findings; re-review required.

A review record claims verification credit ONLY when: independence met,
checklists completed, findings dispositioned, and the record stored under
configuration control.

## Interfaces

- Consumes: allocated requirements (axiom-aerospace-requirements-allocation),
  applicability verdicts (domain standards-applicability skill).
- Delegates technique checks to: axiom-misra-c-cpp-review (coding rules),
  static-analysis / coverage / testing skills for tool evidence.
- Feeds: verification closure (domain verification skill) with review
  records as VERIFIED evidence inputs.

## Acceptance Criteria

- [ ] Review scope, artifact type, and DAL recorded before examination.
- [ ] Independence requirement checked and recorded for DAL A/B items.
- [ ] Every review unit traced to its parent artifact.
- [ ] All checklist gates examined with per-gate outcome.
- [ ] Findings classified DEFECT/QUERY/OBSERVATION with owners.
- [ ] Verdict recorded per the verdict contract above.
- [ ] No DAL assigned, raised, or lowered by the review itself.
- [ ] No normative standard text reproduced in review records.


## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| do178c-review-traceability | DO-178C Cl. 6.3 (reviews and analyses) | HIGH |
| do178c-review-independence | DO-178C Cl. 6.3 (verification independence, DAL A/B) | CRITICAL |
| do178c-review-finding-classification | DO-178C Cl. 6.3 (finding disposition) | MEDIUM |
| do178c-review-dead-code | DO-178C Cl. 6.4 (structural coverage, dead code) | HIGH |
| do178c-review-checklist-completion | DO-178C Cl. 11 (verification evidence) | HIGH |
| do178c-review-verdict-contract | DO-178C Cl. 11 (review records) | HIGH |
| arp4754a-review-system-boundary | ARP4754A Cl. 5 (development process) | MEDIUM |

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
| do178c-review-traceability | HIGH |
| do178c-review-independence | CRITICAL |
| do178c-review-finding-classification | MEDIUM |
| do178c-review-dead-code | HIGH |
| do178c-review-checklist-completion | HIGH |
| do178c-review-verdict-contract | HIGH |
| arp4754a-review-system-boundary | MEDIUM |

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

This skill is the reviewer for aerospace artifacts. It must not modify the
artifact under review; it records findings (DEFECT / QUERY / OBSERVATION) and
a verdict (PASS / CONDITIONAL PASS / FAIL). Independence of the reviewer is a
release gate for DAL A/B items. Solo use requires an explicit waiver recorded
in the deviation log.

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

