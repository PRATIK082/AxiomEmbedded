---
name: validation
description: Needs-based validation scenarios, usability, and acceptance. Use when proving the right product was built for stakeholders.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Validation skill

Confirmation that the right system was built: stakeholder acceptance in the
real operational context against needs and intended use — beyond verification's
"built right" (see `system-test`).

## 1. Purpose and scope

**Purpose.** Demonstrate fitness for intended use with users, operators, and
the real environment, producing the acceptance decision with evidence.

**In scope.** Validation planning, operational scenarios and user workflows,
alpha/beta and field trials, usability and human-factors evaluation,
requirements-vs-needs gap analysis, and the validation report as a release
artifact.

**Non-goals.** Requirement-conformance testing (see `system-test`), unit-level
checks. Starts at an integrated system, ends at stakeholder acceptance.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 15288 | 2023 | Validation process: confirming stakeholder requirements achieved in operation | `https://www.iso.org/standard/81702.html` |
| 2 | ISO 26262-4 | 2018 | §9 vehicle integration and testing including validation at vehicle level | `https://www.iso.org/standard/68386.html` |
| 3 | IEC 62366-1 Medical usability | 2015 + AMD 2020 | Usability engineering for safety-related operator interaction (adopt pattern beyond medical) | `https://webstore.iec.ch/en/publication/6728` |

## 3. Validation rules

1. **Validate against needs, not requirements.** Scenarios derive from
   stakeholder workflows and the operational context (ODD-equivalent for the
   product); passing all system requirements is necessary but not sufficient.
2. **Real environment, real users.** Validation executes with production-
   equivalent hardware, representative operators (not the developers), and
   field conditions. Lab-only validation is a review finding.
3. **Usability is safety-relevant.** Operator error paths (wrong sequence,
   misread display, alarm fatigue) are validated scenarios wherever humans
   interact with safety functions — IEC 62366 pattern: identify use errors,
   mitigate by design, verify mitigations.
4. **Gaps feed requirements.** Every validation finding that is "working as
   specified but wrong for the user" opens a requirements change (see
   `requirements` §5, `change-impact`), not a test waiver.
5. **Acceptance criteria pre-registered.** Pass/fail thresholds and the
   acceptance authority are recorded before the campaign — never negotiated
   after results.

## 4. Exit gates (blocking)

1. Operational scenarios executed in a representative environment by
   representative users.
2. Acceptance criteria met as pre-registered; deviations approved by the
   acceptance authority with rationale.
3. Usability use-errors identified, mitigated, mitigations verified.
4. Needs-gaps converted to requirement changes or formally deferred with owner
   and date.
5. Validation report signed as release evidence.

## 5. Verification of this skill (Phase 4 gate)

- Acceptance criteria pre-date results (audit the timestamps).
- No lab-only validation accepted for operator-facing functions.
