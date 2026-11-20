---
name: axiom-automotive-standards-applicability
title: Automotive Standards Applicability
description: >
  Automotive Standards Applicability workflow for automotive. Use when automotive standards applicability tasks arise in automotive projects.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [automotive]
platforms: [mcu]
axiom:
  dotted_name: axiom.automotive.automotive.standards.applicability
  domain: automotive
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
  primary_domain: automotive
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [iso-26262, iso-sae-21434, automotive-spice, misra-c]
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: []
---

# Axiom Automotive Standards Applicability

## Purpose
Determine which standards apply to an automotive ECU or module project and
record each verdict (APPLICABLE / NOT_APPLICABLE / DEFERRED) with an explicit
rationale. This skill produces an applicability decision -- never a compliance
claim and never a certification.

## When to Use
- At project start, when the standards baseline for an automotive component,
  module, or ECU integration must be fixed.
- When a new standard edition, release, or regulation appears and its effect on
  an in-flight project must be assessed.
- When an auditor, customer, or safety/security plan asks "which standards
  apply here and why".

## When Not to Use
- As certification proof, ASIL assignment, or cybersecurity risk classification.
- As a substitute for reading the actual standard text (this skill works from
  identifiers and applicability metadata only).
- To justify using a draft, proposed, or withdrawn document as a normative basis.

## Required Inputs
- Project context: platform (AUTOSAR Classic / Adaptive / both), target
  AUTOSAR release, MCU / hardware target, software scope (new development,
  integration, maintenance).
- Safety scope statement: whether a functional-safety scope exists and which
  safety plan governs it (if none, ISO 26262-family standards default to
  NOT_APPLICABLE, not to an assumed ASIL).
- Cybersecurity scope statement: whether a cybersecurity scope exists and
  which risk assessment governs it.
- Contractual scope: customer-required processes (e.g. Automotive SPICE),
  type-approval relevance (UNECE R155 / R156), coding-guideline selection.

## Optional Inputs
- Prior applicability matrix for delta assessment.
- Customer or OEM standard handbook references (identifiers only).

## Prerequisites
- `standards/registry.yaml` readable (source of lifecycle states).
- Applicable project plans (safety plan, cybersecurity plan) if their scopes
  are claimed.

## Execution Workflow
1. Capture project context (platform, release, hardware, software scope,
   safety scope, cybersecurity scope, contractual scope). Record unknowns as
   DEFERRED, never as assumptions.
2. Build the candidate list from `standards/registry.yaml`, filtered by family
   (automotive, process, coding, safety, cybersecurity, regulatory).
3. Check lifecycle state per candidate: published documents may be cited as a
   normative basis; pre-release / draft / proposed documents are
   non-normative and must not replace a published edition; withdrawn /
   superseded documents must not be used for new work.
4. Apply applicability rules per candidate:
   - ISO 26262 family: APPLICABLE only when a safety scope and governing
     safety plan exist; ASIL comes from the safety plan, never from this skill.
   - ISO/SAE 21434: APPLICABLE only when a cybersecurity scope and governing
     risk assessment exist.
   - UNECE R155 / R156: APPLICABLE only when vehicle type-approval scope
     includes them.
   - Automotive SPICE: APPLICABLE when contractually required; record the
     agreed PAM version and capability scope.
   - MISRA C / C++ / AUTOSAR C++14: APPLICABLE when the project coding
     guidelines select them; record the exact edition.
   - AUTOSAR platform releases: bind to the exact supplied release; never mix
     Classic, Adaptive, and Foundation versions without a compatibility check.
5. Record every verdict with rationale in the applicability matrix template.
6. Export DEFERRED items and missing-scope items as gaps to the requirements
   baseline; link APPLICABLE standards to follow-on requirements extraction.

## Tool Invocations
- `axiom standards list --family automotive` (inventory candidates).
- `axiom validate-skills --skill <this-skill>` before release.

## Decision Rules
- No safety scope evidence -> ISO 26262 family is NOT_APPLICABLE (never
  "ASIL A by default").
- No cybersecurity scope evidence -> ISO/SAE 21434 is NOT_APPLICABLE.
- Draft / proposed / pre-release document -> may inform, must not norm.
  A draft must never silently replace its published edition.
- Withdrawn / superseded document -> NOT_APPLICABLE for new work; existing
  usage flagged as migration debt.
- Missing context -> DEFERRED with an owner and due date, never assumed.

## Deliverables
- Applicability matrix (`templates/applicability-matrix.md` filled) under the
  module or project evidence directory.
- Gap list of DEFERRED items with owners.

## Acceptance Criteria
- Every candidate standard from the registry filter has a verdict.
- Every APPLICABLE verdict names its governing scope or plan.
- Every NOT_APPLICABLE verdict states its rationale.
- Every DEFERRED verdict names an owner; none is silently assumed.
- No verdict cites a draft/proposed/withdrawn document as normative basis.
- `scripts/validate.py` passes on the filled matrix.

## Validation Procedure
1. `scripts/validate.py --matrix <filled-matrix>` (verdict contract check).
2. `axiom validate-skills --skill axiom-automotive-standards-applicability`.
3. Human review gate for safety/security-relevant verdicts.

## Common Failure Modes
- Assuming ISO 26262 applies "because it is automotive" -> require safety
  scope evidence.
- Citing a draft edition as the requirement basis -> lifecycle check blocks it.
- Copying normative text into the matrix -> identifiers and rationale only.
- Marking everything APPLICABLE to look thorough -> each verdict needs a
  distinct rationale; blanket verdicts fail review.

## Guardrails
- Identifiers, edition numbers, and applicability rationale only. Never copy
  normative clauses, tables, or figures into project files.
- Never claim compliance, certification, ASIL capability, or audit success.
- Safety/security-relevant verdicts require human approval.


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
- Standard identifiers + landing URLs only (see
  `references/standards-map.md`).
