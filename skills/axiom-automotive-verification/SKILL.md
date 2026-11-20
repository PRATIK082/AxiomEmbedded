---
name: axiom-automotive-verification
title: Automotive verification
description: >
  ASPICE SWE.4/SWE.5/SWE.6 requirements-driven verification closure for
  automotive software. Use when proving every allocated software requirement
  is verified with bidirectional traceability, coverage accounting, and a
  machine-checkable verdict.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [automotive]
platforms: [mcu]
axiom:
  dotted_name: axiom.automotive.automotive.verification
  domain: automotive
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [requirement baseline, architecture and design artifacts, test reports and evidence]
  outputs: [verification plan, coverage report, verification verdict record]
  risk_level: medium
  lifecycle: [plan, implement, verify, evidence]
  standards: []
  activity: verification
  capability_kind: domain-specific
  primary_domain: automotive
  risk_class: medium
  lifecycle_phases: [plan, implement, verify, evidence]
  standard_ids: [automotive-spice, iso-26262]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: [axiom-static-analysis-triage, axiom-misra-c-cpp-review, axiom-automotive-code-review, coverage, requirements-traceability]
---

# Axiom Automotive verification

## Purpose
Close the loop between allocated software requirements and verification
evidence. This skill plans verification, accounts for every requirement, and
issues a verdict. It does NOT execute tests itself: test design and execution
belong to the testing skills, static checks belong to the analysis skills.
This skill consumes their reports and proves requirement coverage.

Normative anchors (identifiers only, no normative text reproduced):
- Automotive SPICE 4.1: SWE.4 (software unit verification), SWE.5 (software
  integration and integration test), SWE.6 (software verification).
- ISO 26262: verification planning and work products per the project safety
  plan, where applicable. ASIL values come only from the approved safety plan.

This skill never claims compliance, capability levels, or ASIL compliance.
It produces evidence that a qualified assessor can audit.

## When to Use
- A software requirement baseline (SWE.1) and architecture (SWE.2) exist and
  the project needs a verification plan with full coverage accounting.
- Unit, integration, or qualification test reports exist and someone must
  prove each requirement is VERIFIED, BLOCKED, WAIVED, or NOT_APPLICABLE.
- A change (requirement, design, code, configuration) forces re-verification
  and regression scope must be derived from traceability, not guessed.
- An ASPICE assessment needs SWE.4/SWE.5/SWE.6 work products with explicit
  bidirectional traceability.

## When Not to Use
- As certification proof, ASIL assignment, or a substitute for independent
  assessment.
- As a test-execution engine: delegate unit test design to unit-testing
  skills, integration tests to integration-testing skills, static analysis
  to analysis skills, and MISRA rule checking to axiom-misra-c-cpp-review.
- When no requirement baseline exists: route to axiom-automotive-requirements
  analysis/allocation skills first. Unverifiable requirements are findings,
  not verification scope.

## Required Inputs
- Requirement baseline with stable IDs (from requirements-analysis skill).
- Allocation matrix (from requirements-allocation skill): each requirement
  mapped to its owning component and verification method.
- Architecture and detailed design artifacts under verification.
- Test reports and static-analysis reports to consume (technique skills).
- Safety plan excerpt IF safety-related verification credit is claimed
  (ASIL values and independence requirements only).

## Optional Inputs
- Prior verification verdicts (for regression scoping).
- Change records and defect reports (for re-verification scope).
- Target and toolchain description (for environment adequacy arguments).

## Prerequisites
- Requirements are reviewed and each has at least one acceptance criterion.
- Traceability from requirement to design/code/test stubs exists or its
  absence is recorded as a BLOCKED item, not silently skipped.
- Draft standards never replace published editions for verdict arguments
  (lifecycle gate: draft-must-not-replace-published).

## Execution Workflow
1. Inventory requirements: list every in-scope requirement ID. Mark each
   out-of-scope item NOT_APPLICABLE with written rationale and approval.
2. Confirm verification strategy per requirement: test, analysis, review,
   or a justified combination. One requirement may need several methods.
   Record the method in the verification plan before execution results exist.
3. Check testability: each requirement must have acceptance criteria that a
   test or analysis can objectively pass or fail. Untestable requirements
   are returned as findings to the requirements owner, not waived.
4. Delegate execution: hand test design to testing skills, static analysis
   to analysis skills, interface review to axiom-automotive-code-review.
   Collect their reports as evidence inputs.
5. Account coverage: for each requirement, link the evidence that verifies
   it. Status per requirement: VERIFIED (evidence linked and passing),
   FAILED (evidence linked and failing), BLOCKED (evidence missing or
   environment unavailable, with reason), WAIVED (with justification and
   approval reference), NOT_APPLICABLE (with rationale).
6. Regression on change: given a change record, walk traceability links to
   derive the affected requirement set, then the test set. Re-run scope is
   the derived set, never smaller without written justification.
7. Independence check: safety-related verification must satisfy the
   independence stated in the safety plan (different person, different
   team, or independent organization as required). Record who verified what.
   ASIL values are read from the safety plan, never assigned here.
8. Issue verdict: VERIFIED (all in-scope requirements VERIFIED, waivers
   approved), PARTIAL (failures or blocks remain, listed), or BLOCKED
   (baseline or evidence missing). No silent passes.

## Tool Invocations
- run_skill dry-run first for any delegated test or analysis execution.
- validate_skill gates release of the verification report.
- scripts/validate.py checks the verdict record contract locally.

## Decision Rules
- Every in-scope requirement ends VERIFIED, FAILED, BLOCKED, or WAIVED.
  There is no fifth state and no requirement is dropped silently.
- A waiver requires justification plus an approval reference. Unexplained
  waivers are findings, not verdicts.
- FAILED requirements block a VERIFIED verdict. Retest or fix, then re-run
  this workflow for the affected set.
- Assumptions (environment, stubs, calibration) are listed with owners and
  expiry. Expired assumptions downgrade the verdict to PARTIAL.
- ASIL values come only from the approved safety plan. This skill never
  assigns, upgrades, or downgrades an ASIL.

## Workflow
As Execution Workflow above, recorded in the verification report with the
coverage table as the central artifact.

## Deliverables
- Verification plan: requirement-to-method mapping, environment, schedule
  of verification activities per SWE.4/SWE.5/SWE.6.
- Coverage report: per-requirement status table with evidence links.
- Verification verdict record (templates/verification-record.md): the
  machine-checkable contract validated by scripts/validate.py.
- Gap report: BLOCKED items with owners and due dates.

## Acceptance Criteria
- All in-scope requirements have a status; none are missing or implicit.
- Every VERIFIED requirement links to passing evidence produced by the
  delegated technique skill.
- Every WAIVED and NOT_APPLICABLE item carries justification and approval.
- Independence for safety-related verification matches the safety plan.
- scripts/validate.py passes on the verdict record.
- Checklist checklists/review.yaml is fully green.

## Acceptance
- Same gates, machine-checkable, plus human review of waivers and PARTIAL
  verdicts before release.

## Validation Procedure
- validate_skills plus checklist plus human gate for waivers.
- Re-run scripts/validate.py after any baseline or evidence change.

## Common Failure Modes
- Coverage counted from test names instead of requirement IDs -> always
  anchor on requirement IDs; tests are evidence, not scope.
- Technique reports mistaken for verdicts -> a passing coverage number is
  input, not a verdict. The verdict requires per-requirement accounting.
- Missing inputs invented -> require explicit baselines; BLOCKED is an
  honest status, invention is a defect.
- Change without regression scoping -> any baseline change re-opens step 6.

## Guardrails
- No secrets/shell/net; never claim compliance or capability levels.
- Never assign ASIL values or declare safety case completeness.
- Licensed standard text is never reproduced; identifiers only.


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
- Standard identifiers plus landing URLs only; see
  references/standards-map.md.
