# Unit-Test skill

Isolated verification of software units (functions, classes, modules) with
doubles for hardware and dependencies — the lowest V-model verification level,
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
| 1 | ISO 26262-6 Software level | 2018 | §9 software unit verification, Table 7 methods per ASIL | `https://www.iso.org/standard/68389.html` |
| 2 | DO-178C | 2011 | §6.4 low-level testing, Annex A verification objectives | `https://www.rtca.org/products/software-considerations-in-airborne-systems-and-equipment-certification-do-178/` |
| 3 | ISTQB Certified Tester | CTFL v4.0 (2023) | Unit/component testing principles, coverage types | `https://www.istqb.org/certifications/certified-tester-foundation-level/` |

## 3. Test design rules

1. **One behavior per case.** Test name states input, action, expected outcome;
   a failing test identifies the broken behavior without debugging.
2. **Boundaries and faults first.** Equivalence partitions, boundary values,
   and every error path (null handles, timeouts, CRC failures, queue-full)
   before happy-path variations. Untested error paths are the top unit-test
   defect class.
3. **Doubles with contracts.** Each stub/fake documents what real behavior it
   reproduces and what it simplifies; a double that silently diverges from
   hardware behavior invalidates the test — review doubles like code.
4. **Deterministic.** No sleeps-as-synchronization, no unseeded randomness, no
   order dependence. Same seed, same result, every run, every machine.
5. **Host-first, target-confirmed.** Units run on host CI for speed; coverage
   and timing-sensitive units re-run on target (or instruction-set simulator)
   to confirm compiler/architecture behavior.

## 4. Coverage targets (blocking, per integrity level per `configs/skill-update.yaml`)

| Level | Statement | Branch | MC/DC |
|-------|-----------|--------|-------|
| QM / ASIL A / SIL 1 / DAL D | 100% of new/changed code | 100% | — |
| ASIL B / SIL 2 / DAL C | 100% | 100% | Recommended for safety-critical units |
| ASIL C-D / SIL 3-4 / DAL A-B | 100% | 100% | Required |

Uncovered lines need either a test or a documented justification (defensive
code proven unreachable by analysis, reviewed) — never silence.

## 5. Definition of done (blocking)

1. All new/changed units have tests naming the SwSR they verify.
2. Suite green on host CI and target-confirmation where required.
3. Coverage targets met per §4 with the report archived as evidence.
4. Doubles reviewed; no time-dependent or order-dependent cases.
5. Failures link to defects; no test disabled without a tracked waiver.

## 6. Verification of this skill (Phase 4 gate)

- Coverage claims reference measured reports, not estimates.
- Disabled tests without waivers fail the gate.
