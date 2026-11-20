---
name: system-test
description: >
  Requirement-based system testing, stress/abuse campaigns, and triage. Use when
  validating a full product against its requirements.
version: 1.3.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.system-test
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy, vv, system]

  related_skills: [axiom-hil-test-planning, axiom-test-automation, axiom-validation-orchestrator]
  checklists: [checklists/system-test-checklist.md]

  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: []
  optional_tools: []
---

# System-Test skill

End-to-end verification of the integrated system against system requirements in
a representative environment -- the top of the V-model right arm before
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
| 1 | ISO 26262-4 System level | 2018 | S8 system testing, S9 verification reviews per ASIL | `https://www.iso.org/standard/68386.html` |
| 2 | ISO/IEC/IEEE 29119 Software testing | 29119-1:2022 concepts, 29119-2:2021 processes | Test planning, design, execution, and reporting processes | `https://www.iso.org/standard/81291.html` |
| 3 | ISTQB Certified Tester | CTFL v4.0 (2023) | System test objectives, entry/exit criteria, defect lifecycle | `https://www.istqb.org/certifications/certified-tester-foundation-level/` |

## 3. Test design rules

1. **Requirement-based, risk-ordered.** `[CRITICAL]` Every system requirement
   has at least one test; safety/security requirements first, then timing, then
   functional breadth. Coverage of requirements (not code) is the system-test
   metric.
2. **Environment fidelity stated.** `[HIGH]` Each campaign records how the
   environment differs from production (chamber vs field, simulated vs real load)
   and why the difference does not invalidate the result. Unstated fidelity gaps
   are review findings.
3. **Stress to the limit, then beyond.** `[HIGH]` Thermal, voltage, vibration,
   EMI, load, and longevity campaigns establish margins -- passing at nominal
   only proves the demo works.
4. **Abuse cases.** `[CRITICAL]` Wrong inputs, failed sensors, power loss,
   operator error, hostile network traffic: the system must reach a safe state
   or degrade gracefully per the safety goals (`safety` S4), never undefined
   behavior.
5. **Regression is automatic.** `[HIGH]` The system regression suite runs on
   every release candidate; manual-only regression does not scale past prototype
   and blocks release.

## 4. Defect triage

Severity derives from requirement impact: safety-requirement violation or safe-
state failure = critical (blocks release unconditionally); timing violation =
major; cosmetic = minor. No critical or major defects open at release; waivers
require integrity-level-appropriate approval with compensating measures and
expiry.

## 5. Advanced V&V patterns (P1)

### 5.1 Multi-DUT testing `[HIGH]`
Synchronized multi-DUT logic with per-device options; required for gateway,
multi-node, and redundancy system scenarios.

### 5.2 Keyword layered architecture `[MEDIUM]`
Protocol-level Python driver libraries plus domain keywords (Robot Framework
shape): thin keywords over drivers, resource files per bench, variable files
per board. Same suite runs in SIL and HIL.

### 5.3 RF remote execution `[MEDIUM]`
Parallel execution with pabot, result merge with Rebot, remote servers for
distributed benches. Required for large system suites exceeding the feedback
budget.

### 5.4 Firmware provisioning in CI `[HIGH]`
Automated flash of attested firmware before system tests; hash recorded and
gated in pre-check. No system test runs on an unattested image.

### 5.5 Flash caching `[MEDIUM]`
Hash-based skip-reflash when the attested image is already present; reduces
bench time. Cache invalidates on hash mismatch or policy change.

### 5.6 Panic/core-dump decoding `[HIGH]`
Automated backtrace decode on failure (addr2line/elf tools); attach decoded
trace to the defect. Required for any crash during system campaign.

### 5.7 RESD sensor replay `[MEDIUM]`
Deterministic replay of recorded sensor streams for reproducible system-level
fault and abuse cases.

## 6. Exit gates (blocking)

1. 100% of system requirements executed with pass results; failures triaged
   per S4 with zero critical/major open.
2. Stress and abuse campaigns complete with margin results recorded.
3. Environment fidelity statement reviewed and accepted.
4. Regression suite automated and green on the release candidate.
5. System-test report signed as release evidence (`evidence` skill).

## 7. Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| ST-R1 | ISO 26262-4 S8 | System testing per ASIL |
| ST-R2 | ISO/IEC/IEEE 29119-1/2 | Test planning and reporting |
| ST-R3 | ISTQB CTFL v4.0 | System test objectives and defect lifecycle |

## 8. Verification of this skill (Phase 4 gate)

- Requirement coverage measured and complete -- code coverage is not a
  substitute at this level.
- Open critical/major defects block the gate unconditionally.

## Workflow

Follow the skill's numbered rules and gates; record per-step evidence in the
run manifest.

## Acceptance

All checklist gates pass; findings carry severity plus evidence plus action.


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

- `references/standard-map.md`
- `references/vv-patterns.md`
