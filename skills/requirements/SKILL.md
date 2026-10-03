---
name: requirements
description: Elicitation and baselining of verifiable requirements with methods, allocation, and traceability. Use when writing specs, SHALL statements, or baselining scope.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Requirements skill

Elicitation, specification, and management of requirements for embedded and
cyber-physical systems — the V-model left-arm foundation every downstream
artifact traces to.

## 1. Purpose and scope

**Purpose.** Produce requirements that are verifiable, traced, and change-
controlled, so architecture, code, and tests always answer to a known baseline.

**In scope.** Stakeholder elicitation, system/software requirements derivation
and allocation, quality attributes (timing, safety, security, power),
requirements modeling (SysML/UML), baseline management, and change control.

**Non-goals.** Product discovery and market analysis. This skill starts when a
need exists and ends with a baselined, reviewed specification.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 29148 Requirements engineering | 2018 | Requirements processes, characteristics of good requirements, traceability | `https://www.iso.org/standard/72089.html` |
| 2 | ISO/IEC/IEEE 15288 System life cycle processes | 2023 (3rd ed.) | Stakeholder needs, requirements definition, architecture definition processes | `https://www.iso.org/standard/81702.html` |
| 3 | INCOSE Guide to Writing Requirements | v4.0 (2023) | Requirement statement patterns, verification-oriented wording | `https://www.incose.org/products-and-services/technical-products/guide-to-writing-requirements` |
| 4 | ISO 26262-8 Supporting processes | 2018 | Clause 6 requirements management, change and configuration discipline for safety | `https://www.iso.org/standard/68390.html` |

## 3. Requirement quality rules

Every requirement is a single verifiable statement: subject + capability +
condition + measurable criterion. Rules:

1. **Atomic and singular.** One "shall" per requirement; no "and/or" bundles.
2. **Measurable.** Each requirement names its tolerance, bound, or threshold
   (timing in ms, accuracy in %, current in mA). Unquantified adjectives
   ("fast", "robust", "user-friendly") are defects.
3. **Verifiable method assigned at creation.** Each requirement declares its
   verification method — test, analysis, inspection, or demonstration (see
   `system-test`, `validation`). A requirement with no method is a draft,
   never baselined.
4. **Traced both directions.** Stakeholder need → system requirement → software
   requirement → architecture element → test case, recorded in
   `schemas/traceability-matrix.schema.json`. Orphan or childless requirements
   block baselining.
5. **Change-controlled.** Baselined requirements change only via change request
   with impact analysis (see `change-impact`): affected design, code, tests,
   and evidence listed before approval.

## 4. Allocation to embedded concerns

System requirements allocate explicitly across the disciplines this program
covers — each allocation names its owner skill:

- Timing/deadlines → `rtos` (§5 WCET) or `mcu` (bare-metal budgets)
- Safety integrity → `safety` (§3 ASIL/SIL/DAL, §4 FSR/TSR/SwSR chain)
- Security properties → `security` (threat model, secure boot per
  `embedded-linux` §6)
- Power/thermal envelopes → `mcu` / `hardware-architecture`
- ML behavior bounds → `ai-validation` (ODD, §3)

Unallocated system requirements are a blocking review finding.

## 5. Baselining gates (blocking)

1. Every requirement atomic, quantified, with an assigned verification method.
2. Bidirectional traceability gap-free in the traceability matrix.
3. All system requirements allocated to a discipline owner.
4. Review dispositions recorded; safety/security requirements reviewed with
   independence per their integrity level.
5. Change-control procedure active on the baseline from sign-off onward.

## 6. Verification of this skill (Phase 4 gate)

- Normative sources carry number + version + clause + URL (§2).
- No baselined requirement without method, allocation, and trace links (§3–§5).
