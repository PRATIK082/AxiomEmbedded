# Implementation skill

Turning evaluated architecture into verified code: coding standards, construction
practices, static analysis, peer review, and unit verification for C, C++, and
Rust firmware and embedded software.

## 1. Purpose and scope

**Purpose.** Produce code that is correct, readable, statically clean, reviewed,
and unit-verified — ready for integration (`integration-test`) with evidence
attached.

**In scope.** Language-specific construction rules (C/C++/Rust), MISRA and CERT
adherence, static analysis configuration and deviation handling, code review
practice, unit design for testability, and the definition-of-done for a merged
change.

**Non-goals.** System architecture (see `architecture`), integration/system test
strategy (see `integration-test`, `system-test`). Starts at an allocated
software requirement, ends at a reviewed, statically clean, unit-tested commit.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | MISRA C | MISRA C:2025 (March 2025, current); C:2023 baseline | Mandatory/required/advisory rules for safety-related C | `https://misra.org.uk/` |
| 2 | MISRA C++ | MISRA C++:2023 (C++17, merged AUTOSAR C++) | Safety-related C++ subset | `https://misra.org.uk/` |
| 3 | CERT C / C++ | Current rule sets | Secure-coding rules mapped by MISRA Addendum 3 (Jan 2025) | `https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard` |
| 4 | MISRA Rust | In development (working group; guidelines emerging) | Track status; apply CERT-style discipline meanwhile — record status honestly | `https://misra.org.uk/misra-rust/` |

> Version honesty. Cite MISRA C:2025 for new work; C:2023 baselines stay valid
> for in-flight projects with a recorded migration decision. MISRA Rust is not
> published — never claim compliance with it.

## 3. Construction rules (language-neutral)

1. **Small units.** Functions fit on a screen (≤60 lines default), single
   purpose, ≤5 parameters; complexity ≤15 enforced by `rules/skill-update-gates.yaml`.
2. **No hidden behavior.** No recursion in constrained targets, no dynamic
   allocation after init (see `mcu`, `rtos`), no unspecified evaluation-order
   dependence, all variables initialized at declaration.
3. **Errors are values.** Every fallible operation returns a status the caller
   must handle; ignored return values are blocking review findings. Define the
   project's error taxonomy once (per module or globally) and use it uniformly.
4. **Concurrency by design.** Shared state minimized; ISRs and tasks communicate
   via queues with ownership rules (see `rtos`); data races are treated as
   defects, not timing quirks — verify with thread sanitizers or model checks
   where the target toolchain permits.
5. **Testability built in.** Hardware dependencies injected behind interfaces
   (HAL mocks, link-time stubs); untestable-by-construction code requires a
   waiver with an integration-test plan, not silence.

## 4. Static analysis and deviations

1. **Clean on every commit.** MISRA + CERT checkers run in CI with zero new
   violations; the build fails on any finding (warnings-as-errors discipline
   per `configs/skill-update.yaml`: `-Wall -Wextra -Werror`, gcc + clang).
2. **Deviations are documents.** Each deviation records rule ID, rationale,
   safety/security impact review, expiry or review date, and approver — stored
   in `schemas/compliance-evidence.schema.json` (`deviations`). Undocumented
   suppressions (`// NOLINT` without a deviation ID) are defects.
3. **Rust posture.** Memory-safety by ownership; `unsafe` blocks minimized,
   each with a documented invariant and review by a second engineer; MISRA Rust
   tracked for adoption when published.

## 5. Review and definition of done

Peer review checks: requirement trace, error handling, concurrency safety,
resource bounds, test coverage of new branches, and deviation validity. A
merged change is done only when: reviewed with dispositions, statically clean,
unit-tested to the coverage target of its ASIL/SIL/DAL (`unit-test`), and
traced in the matrix.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL (§2); no MISRA-Rust
  compliance claims.
- Zero undocumented suppressions; every merge meets §5.
