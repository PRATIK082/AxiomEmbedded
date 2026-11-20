---
name: axiom-aerospace-requirements-analysis
title: Aerospace Requirements Analysis
description: >
  Analyzes aircraft and system requirements and flows them down to software
  high-level requirements (HLR) per ARP4754A and DO-178C, with DAL provenance
  from the ARP4761 safety assessment. Use when airborne software requirements
  analysis or HLR flow-down is required.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [aerospace]
platforms: [mcu, mpu]

axiom:
  dotted_name: axiom.aerospace.requirements.analysis
  domain: aerospace
  subdomain: aerospace
  category: requirements
  maturity: experimental
  owner: axiom-embedded
  tags: [requirements-analysis]
  activity: requirements-analysis
  capability_kind: domain-specific
  primary_domain: aerospace
  risk_class: medium
  lifecycle_phases: [discover, plan, implement, verify, evidence]
  standard_ids: [arp4754, do-178c]
  artifact_types: [report, manifest]

  related_skills:
    - axiom-aerospace-requirements-allocation
    - axiom-aerospace-verification
    - axiom-aerospace-standards-applicability
    - axiom-aerospace-do178c-workflow

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [arp4754, do-178c]
  artifact_types: [analysis report, HLR set, gap report, baseline record]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  inputs:
  - repository path
  - target files
  - objective
  - constraints
  outputs:
  - run report
  - run manifest
  required_tools:
  - validate_skill
  optional_tools:
  - run_skill
---
# Aerospace Requirements Analysis

## Scope
This skill governs analysis of aircraft and system requirements and their
flow-down to software high-level requirements (HLR) for airborne systems.
It applies ARP4754A system development processes and DO-178C software
planning aspects to requirements capture, validation, and traceability.
It covers stakeholder needs, system requirements, HLR derivation, and
the safety-assessment interface (ARP4761) that drives DAL assignment.

## Inputs
- Aircraft or system requirements allocated to software (with source ID)
- Applicable standards baseline record (registry IDs only)
- Safety assessment outputs affecting requirements (FHAs, preliminary DAL)
- Requirement management tool export or requirements document
- Stakeholder list and review authority matrix

## Rules
- Never invent requirement IDs, DAL values, or failure condition classifications.
- A Development Assurance Level (DAL A-E) comes only from the approved safety
  assessment process (ARP4761); analysis must not assign or assume a DAL.
- HLR characteristics follow DO-178C: unambiguous, verifiable, consistent,
  traceable, and conforming to standards. Each HLR traces to system requirement(s).
- Derived requirements (not directly traceable to a higher requirement) must be
  explicitly flagged and provided to the safety process for assessment.
- Do not reproduce normative text from licensed standards; cite document
  identifiers, section numbers, and requirement references only.
- Every requirement carries status: NEW, ANALYZED, REVIEWED, BASELINED,
  CHANGED, or DEFERRED. Changed HLRs re-enter safety assessment impact review.
- Draft or superseded standard editions must not replace the project's
  approved baseline (lifecycle gate: draft-must-not-replace-published).

## Workflow
1. Collect source requirements: record document ID, revision, section, page.
2. Validate completeness: every system requirement allocated to software is
   accounted for; gaps become UNRESOLVED items with owners.
3. Derive HLRs: write verifiable statements; link each HLR to parent
   system requirement(s); flag derived requirements.
4. Interface with safety: submit derived/new requirements to the safety
   assessment; record assigned DAL per software item or HLR group.
5. Verify HLR characteristics: review for ambiguity, consistency,
   verifiability, and traceability (feeds the verification skill).
6. Baseline: record approval authority, date, and tool baseline ID.
7. Change control: assess impact of each change on traceability, DAL
   applicability, and verification credit; re-baseline.

## Outputs
- Requirements analysis report (per system/software item)
- HLR set with parent traceability and derived-requirement flags
- Gap report (UNRESOLVED items with owners and due dates)
- Safety assessment interface record (submitted items, assigned DALs)
- Baseline record (authority, date, tool ID)

## Acceptance Criteria
- 100 percent of allocated system requirements are traced to HLRs or
  recorded as gaps with owners.
- Every HLR has at least one parent link or an explicit derived flag.
- All derived requirements have a safety assessment disposition.
- No DAL value appears without safety assessment provenance.
- Baseline record is signed by the review authority.

## Failure Modes
- Missing parent requirements: analysis proceeds on assumed sources. STOP,
  record UNRESOLVED, escalate to systems engineering.
- Safety assessment unavailable: DAL-dependent planning is BLOCKED; only
  DAL-independent analysis may proceed, marked accordingly.
- Conflicting stakeholder needs: record conflict, propose options, obtain
  decision; never silently resolve in favor of one party.

## Related Skills
- axiom-aerospace-requirements-allocation (allocation of HLRs to architecture)
- axiom-aerospace-verification (reviews, analyses, and tests of HLRs)
- axiom-aerospace-standards-applicability (standards baseline verdicts)
- axiom-aerospace-do178c-workflow (lifecycle planning context)


## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| arp4754a-req-system-to-hlr | ARP4754A Cl. 5 (development process) | HIGH |
| do178c-req-hlr-characteristics | DO-178C Cl. 5 (software high-level requirements) | HIGH |
| do178c-req-derived-flag | DO-178C Cl. 5 (derived requirements) | MEDIUM |
| arp4761-req-dal-provenance | ARP4761 (safety assessment process) | CRITICAL |
| do178c-req-baseline-control | DO-178C Cl. 7 (software configuration management) | MEDIUM |
| do178c-req-normative-text | Copyright-safe standards (no normative text) | MEDIUM |

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
| arp4754a-req-system-to-hlr | HIGH |
| do178c-req-hlr-characteristics | HIGH |
| do178c-req-derived-flag | MEDIUM |
| arp4761-req-dal-provenance | CRITICAL |
| do178c-req-baseline-control | MEDIUM |
| do178c-req-normative-text | MEDIUM |

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

This skill is a builder for requirements analysis. Its outputs must be
independently checked by its paired reviewer (axiom-aerospace-code-review for
artifact reviews) before acceptance. Solo use requires an explicit waiver
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

