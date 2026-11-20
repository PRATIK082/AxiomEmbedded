---
name: axiom-automotive-code-review
title: Automotive Code Review
description: >
  ASPICE SWE.5/SWE.6-aligned peer review for automotive C/C++ (MISRA C, AUTOSAR C++14):
  review planning, ASIL-aware sampling, reviewer independence, safety-related change
  review, and verification evidence. Invokes axiom-misra-c-cpp-review for rule-level
  checking. Use when automotive code must pass peer review before integration.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [automotive]
platforms: [mcu]
axiom:
  dotted_name: axiom.automotive.automotive.code.review
  domain: automotive
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [repository path, review scope, ASIL scope, objective, constraints]
  outputs: [review record, defect list, review verdict]
  risk_level: medium
  lifecycle: [implement, verify, evidence]
  standards: []
  activity: code-review
  capability_kind: domain-specific
  primary_domain: automotive
  risk_class: medium
  lifecycle_phases: [implement, verify, evidence]
  standard_ids: [misra-c, autosar-cpp14, iso-26262]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: [axiom-misra-c-cpp-review, code-review]
---

# Axiom Automotive Code Review

## Purpose

Process-level peer review for safety-related automotive software. This skill plans,
executes, and records code reviews that satisfy Automotive SPICE SWE.5 (software
qualification test is separate) review expectations and SWE.6 verification, without
claiming certification. Rule-level MISRA checking is delegated to
`axiom-misra-c-cpp-review`; this skill owns scope, sampling, independence,
severity judgement, and evidence.

## When to Use

- A module reaches implementation-complete and needs peer review before
  component integration (SWE.5 entry gate).
- A safety-related change (ASIL B and above) modifies reviewed code.
- A review verdict (READY / REWORK / BLOCKED) is required as release evidence.
- Review coverage must be demonstrated for an ASPICE assessment sample.

## When Not to Use

- As a substitute for static analysis, unit testing, or a qualified safety
  assessment. A review verdict is not an ASIL sign-off.
- As certification proof of any kind.

## Required Inputs

- Repository path and review scope (files, translation units, change set).
- Module manifest: platform, AUTOSAR release, ASIL scope (from the project safety
  plan, never assigned by this skill).
- Coding standard in force (MISRA C version, AUTOSAR C++14 subset, project deviations).
- Prior review records for the same scope (for re-review delta scoping).

## Review Dimensions

1. **Requirements linkage.** Every reviewed unit must trace to an allocated
   software requirement or carry an explicit UNREVIEWED waiver with rationale.
2. **Interface contracts.** API signatures, parameter ranges, error codes, buffer
   ownership, reentrancy and interrupt-context restrictions checked against the
   interface specification -- not against the implementation's own comments.
3. **Rule compliance.** Delegate to `axiom-misra-c-cpp-review`; record tool,
   version, rule set, and unresolved deviations. Undeviated mandatory violations
   are BLOCKED by default.
4. **Defensive behavior.** Error paths, boundary values, resource exhaustion,
   timeout and recovery paths reviewed with the same rigor as nominal paths.
5. **Safety-related changes.** Any change touching a safety mechanism, diagnostic
   path, or fault handler triggers full re-review of the affected unit plus an
   impact note on dependent modules.
6. **Generated vs handwritten.** Generated code is reviewed by validating the
   generator input and template version, never by editing generated output.

## Independence and Sampling

- The author of a unit under review cannot be its sole reviewer. For ASIL C/D
  scope, at least one reviewer must be organisationally independent of the
  implementation task.
- Sampling must be justified in the review record: 100% for new safety-related
  units; risk-based sampling for non-safety code with the sampling rationale
  recorded. Never claim full review coverage from a sample.

## Execution Workflow

1. Normalize the request: scope, ASIL context, coding standard, prior records.
2. Confirm traceability: requirement-to-unit mapping present or gaps logged.
3. Run rule-level check via `axiom-misra-c-cpp-review`; collect findings.
4. Review interface contracts, error handling, and safety-related deltas.
5. Classify each defect: BLOCKED (safety impact or mandatory violation),
   REWORK (must fix before integration), ADVISORY (fix or deviate with rationale).
6. Record the verdict: READY, REWORK, or BLOCKED -- with evidence references.
7. On re-review, scope to the delta plus affected interfaces; close defects
   explicitly with fix references.

## Outputs

- Review record: scope, reviewers and independence statement, standard and tool
  versions, sampling rationale, defect list with severities, verdict.
- Defect list mapped to files, functions, requirements, and (for rule findings)
  MISRA rule IDs.
- Gap report: untraceable units, missing prior records, unresolvable findings
  marked BLOCKED with evidence.

## Acceptance Criteria

- A review record exists for the scope and passes `scripts/validate.py`.
- Every checklist gate in `checklists/review.yaml` is satisfied or has a
  recorded waiver with rationale.
- The verdict is consistent with the defect list (no READY with open BLOCKED).
- ASIL C/D scopes name an independent reviewer in the record.

## Decision Rules

- No verdict without evidence references. A claim of READY with open BLOCKED
  defects is invalid.
- Do not invent ASIL classifications, rule IDs, or requirement references.
- Flag every assumption; safety/security-relevant output requires human review.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| review-independence | Automotive SPICE 4.x SWE.5 (peer review) | HIGH |
| review-asil-sampling | ISO 26262-6:2018 Cl. 8 (software unit implementation) | CRITICAL |
| review-misra-delegation | MISRA C:2012 (mandatory rules) / AUTOSAR C++14 | HIGH |
| review-generated-code | Automotive SPICE 4.x SWE.3 (software detailed design) | MEDIUM |
| review-defect-classification | Automotive SPICE 4.x SWE.5 BP (defect management) | MEDIUM |
| review-evidence-record | ISO 26262-8:2018 Cl. 9 (safety case) | HIGH |

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
| review-independence | HIGH |
| review-asil-sampling | CRITICAL |
| review-misra-delegation | HIGH |
| review-generated-code | MEDIUM |
| review-defect-classification | MEDIUM |
| review-evidence-record | HIGH |

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

