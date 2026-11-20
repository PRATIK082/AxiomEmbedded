---
name: unit-test
description: >
  Host/target unit testing with mocks, coverage per integrity level, and done
  criteria. Use when writing module tests or setting coverage targets.
version: 1.3.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.unit-test
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy, vv, unit]

  related_skills: [axiom-test-automation, axiom-validation-orchestrator]
  checklists: [checklists/unit-test-checklist.md]

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

# Unit-Test skill

Isolated verification of software units (functions, classes, modules) with
doubles for hardware and dependencies -- the lowest V-model verification level,
executed on host with coverage measured against the integrity target.

## 1. Purpose and scope

**Purpose.** Prove each unit satisfies its SwSR with repeatable host-executed
tests that run in milliseconds and gate every commit.

**In scope.** Test frameworks (Unity/Ceedling, CppUTest, GoogleTest, Rust
`cargo test`), doubles (stubs, fakes, mocks), host-vs-target strategy, coverage
measurement (statement/branch/MC-DC), and test-review discipline.

**Non-goals.** Integration of units (see `integration-test`), hardware
interaction (see `system-test`, `hardware-bringup`).

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-6 Software level | 2018 | S9 software unit verification, Table 7 methods per ASIL | `https://www.iso.org/standard/68389.html` |
| 2 | DO-178C | 2011 | S6.4 low-level testing, Annex A verification objectives | `https://www.rtca.org/products/software-considerations-in-airborne-systems-and-equipment-certification-do-178/` |
| 3 | ISTQB Certified Tester | CTFL v4.0 (2023) | Unit/component testing principles, coverage types | `https://www.istqb.org/certifications/certified-tester-foundation-level/` |

## 3. Test design rules

1. **One behavior per case.** `[HIGH]` Test name states input, action, expected
   outcome; a failing test identifies the broken behavior without debugging.
2. **Boundaries and faults first.** `[CRITICAL]` Equivalence partitions,
   boundary values, and every error path (null handles, timeouts, CRC failures,
   queue-full) before happy-path variations. Untested error paths are the top
   unit-test defect class.
3. **Doubles with contracts.** `[HIGH]` Each stub/fake documents what real
   behavior it reproduces and what it simplifies; a double that silently
   diverges from hardware behavior invalidates the test -- review doubles like
   code.
4. **Deterministic.** `[CRITICAL]` No sleeps-as-synchronization, no unseeded
   randomness, no order dependence. Same seed, same result, every run, every
   machine.
5. **Host-first, target-confirmed.** `[MEDIUM]` Units run on host CI for speed;
   coverage and timing-sensitive units re-run on target (or instruction-set
   simulator) to confirm compiler/architecture behavior.

## 4. Coverage targets (blocking, per integrity level per `configs/skill-update.yaml`)

| Level | Statement | Branch | MC/DC |
|-------|-----------|--------|-------|
| QM / ASIL A / SIL 1 / DAL D | 100% of new/changed code | 100% | -- |
| ASIL B / SIL 2 / DAL C | 100% | 100% | Recommended for safety-critical units |
| ASIL C-D / SIL 3-4 / DAL A-B | 100% | 100% | Required |

Uncovered lines need either a test or a documented justification (defensive
code proven unreachable by analysis, reviewed) -- never silence.

## 5. Definition of done (blocking)

1. All new/changed units have tests naming the SwSR they verify.
2. Suite green on host CI and target-confirmation where required.
3. Coverage targets met per S4 with the report archived as evidence.
4. Doubles reviewed; no time-dependent or order-dependent cases.
5. Failures link to defects; no test disabled without a tracked waiver.

## 6. Advanced V&V patterns (P1)

### 6.1 Sanitizer gates `[HIGH]`
Run ASan/UBSan/LSan on the host unit suite in CI; treat any finding as a
build failure. Emit SARIF for triage. Required for all C/C++ units; optional
for Rust (Miri for unsafe).

### 6.2 Fuzzing lifecycle `[HIGH]`
Coverage-guided fuzzer (libFuzzer/AFL++) harness per parser/state-machine
unit. Maintain a seed corpus in-repo; triage crashes into minimal reproducers
and regression tests. Run nightly or on PRs touching parsers.

### 6.3 Property-based testing `[HIGH]`
Use property tests (Hypothesis/QuickCheck style) for arithmetic, codecs, and
protocol parsers. Define invariants (round-trip, idempotence, monotonicity)
rather than example cases; shrink failures to minimal counterexamples.

### 6.4 Mutation testing `[MEDIUM]`
Run mutation testing (mutmut/pitest/cargo-mutants) on safety-critical units;
surviving mutants require either a new test or a documented justification.
Gate on mutation score per integrity level.

### 6.5 Death tests `[MEDIUM]`
For error-handling paths, assert that the unit aborts/fails safely under
invalid input (GoogleTest death-test pattern). Required where defensive checks
are the safety mechanism.

## 7. Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| UT-R1 | ISO 26262-6 S9, Table 7 | Unit verification methods per ASIL |
| UT-R2 | DO-178C S6.4, Annex A | Low-level test objectives |
| UT-R3 | ISTQB CTFL v4.0 | Component test principles |

## 8. Verification of this skill (Phase 4 gate)

- Coverage claims reference measured reports, not estimates.
- Disabled tests without waivers fail the gate.
- Sanitizer/fuzz/property/mutation evidence archived where applicable.

## Workflow

Follow the skill's numbered rules and gates; record per-step evidence in the
run manifest.

## Acceptance

All checklist gates pass; findings carry severity plus evidence plus action.

## References

- `references/standard-map.md`
- `references/vv-patterns.md` (advanced V&V pattern detail)
