# System-Test skill

End-to-end verification of the integrated system against system requirements in
a representative environment — the top of the V-model right arm before
acceptance and validation.

## 1. Purpose and scope

**Purpose.** Prove the complete system (hardware + software + mechanics +
operators + environment) satisfies its system requirements under nominal,
stressed, and abused conditions.

**In scope.** System test planning, environment fidelity (test tracks, chambers,
fleet pilots), requirement-based test design, stress/robustness campaigns,
regression strategy, defect triage with severity tied to requirements, and the
system-test report as a release artifact.

**Non-goals.** Unit/integration verification (see `unit-test`,
`integration-test`), stakeholder acceptance in the operational context (see
`validation`).

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-4 System level | 2018 | §8 system testing, §9 verification reviews per ASIL | `https://www.iso.org/standard/68386.html` |
| 2 | ISO/IEC/IEEE 29119 Software testing | 29119-1:2022 concepts, 29119-2:2021 processes | Test planning, design, execution, and reporting processes | `https://www.iso.org/standard/81291.html` |
| 3 | ISTQB Certified Tester | CTFL v4.0 (2023) | System test objectives, entry/exit criteria, defect lifecycle | `https://www.istqb.org/certifications/certified-tester-foundation-level/` |

## 3. Test design rules

1. **Requirement-based, risk-ordered.** Every system requirement has at least
   one test; safety/security requirements first, then timing, then functional
   breadth. Coverage of requirements (not code) is the system-test metric.
2. **Environment fidelity stated.** Each campaign records how the environment
   differs from production (chamber vs field, simulated vs real load) and why
   the difference does not invalidate the result. Unstated fidelity gaps are
   review findings.
3. **Stress to the limit, then beyond.** Thermal, voltage, vibration, EMI,
   load, and longevity campaigns establish margins — passing at nominal only
   proves the demo works.
4. **Abuse cases.** Wrong inputs, failed sensors, power loss, operator error,
   hostile network traffic: the system must reach a safe state or degrade
   gracefully per the safety goals (`safety` §4), never undefined behavior.
5. **Regression is automatic.** The system regression suite runs on every
   release candidate; manual-only regression does not scale past prototype and
   blocks release.

## 4. Defect triage

Severity derives from requirement impact: safety-requirement violation or safe-
state failure = critical (blocks release unconditionally); timing violation =
major; cosmetic = minor. No critical or major defects open at release; waivers
require integrity-level-appropriate approval with compensating measures and
expiry.

## 5. Exit gates (blocking)

1. 100% of system requirements executed with pass results; failures triaged
   per §4 with zero critical/major open.
2. Stress and abuse campaigns complete with margin results recorded.
3. Environment fidelity statement reviewed and accepted.
4. Regression suite automated and green on the release candidate.
5. System-test report signed as release evidence (`evidence` skill).

## 6. Verification of this skill (Phase 4 gate)

- Requirement coverage measured and complete — code coverage is not a
  substitute at this level.
- Open critical/major defects block the gate unconditionally.
