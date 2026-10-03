---
name: rust-embedded
description: no_std setup, unsafe-review policy, FFI ownership rules. Use when writing Rust firmware or mixing Rust with C.
version: 1.2.0
domains: [all]
platforms: [mcu, mpu, bare-metal, rtos]
---

# Rust-Embedded skill

Memory-safe firmware in Rust for MCU/MPU targets: ownership-based driver
design, `no_std` ecosystem use, `unsafe` confinement with documented
invariants, and interoperability with C codebases — with standards-status
honesty until MISRA Rust publishes.

## 1. Purpose and scope

**Purpose.** Exploit Rust's ownership model to eliminate memory-safety defect
classes (use-after-free, data races, buffer overruns) in new firmware while
integrating pragmatically with existing C HALs and toolchains.

**In scope.** `no_std` project setup, HAL/PAC layering (`embedded-hal` traits),
`unsafe` policy, FFI with C, panic strategy, RTIC vs RTOS task models, and the
review discipline specific to Rust firmware.

**Non-goals.** Rewriting proven C drivers without cause; `std` applications on
embedded Linux (use normal Rust practice plus `embedded-linux`). This skill
complements `embedded-c`, it does not mandate replacement.

## 2. Normative sources (high confidence, status-labeled)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | The Rust Reference / Edition 2021+ | Current stable | Language semantics baseline | `https://doc.rust-lang.org/reference/` |
| 2 | Embedded Rust Book (`no_std`) | Current | `no_std` setup, peripherals, allocators, panic behavior | `https://docs.rust-embedded.org/book/` |
| 3 | `embedded-hal` traits | 1.0 (stable) | Portable driver interfaces across MCUs | `https://docs.rs/embedded-hal/` |
| 4 | MISRA Rust | **In development, unpublished** | Track for adoption; do NOT claim compliance | `https://misra.org.uk/misra-rust/` |

> Status honesty (blocking rule). Any claim of "MISRA-compliant Rust" before
> publication is a false claim. Cite this table's status labels in evidence.

## 3. Project setup rules

1. **Pinned toolchain.** `rust-toolchain.toml` pins the exact stable release;
   `cargo auditable` / lockfile committed; no floating nightly without a
   recorded reason and CI pin.
2. **Panic policy decided once.** `panic = "abort"` with a documented reset or
   safe-state path for constrained targets; unwinding only where the runtime
   and analysis support it. Panic paths are tested (trigger + observe safe
   behavior), never "cannot happen".
3. **No `std` leakage.** `no_std` + `no_main`; `alloc` only with a proven
   allocator and the same no-alloc-after-init rule as C/C++ (`rtos` §5).

## 4. `unsafe` policy (the core of this skill)

1. **Confinement.** `unsafe` appears only in low-level register access, FFI,
   and vetted synchronization primitives — never in application logic.
2. **Documented invariants.** Every `unsafe` block carries a `// SAFETY:`
   comment stating the invariant the author upholds (alignment, validity,
   exclusive access, lifetime) — missing SAFETY comments are blocking findings.
3. **Second-eyes review.** All `unsafe` code requires a second reviewer; new
   `unsafe` in safety-relevant paths additionally requires the rationale in an
   ADR and coverage in `safety` evidence.
4. **Minimize via PACs.** Prefer vendor PAC crates and `embedded-hal`
   implementations over hand-rolled register code; hand-rolled MMIO needs a
   justification (missing PAC, proven PAC defect).

## 5. FFI and mixed C/Rust projects

1. **Boundary ownership.** C↔Rust interfaces use `repr(C)`, ownership transfer
   documented per function (who allocates, who frees, valid lifetimes);
   `bindgen` output reviewed, not blindly trusted.
2. **Incremental adoption path.** New drivers in Rust behind `embedded-hal`
   traits; proven C drivers stay until a defect, portability, or safety case
   motivates the rewrite — recorded per module, not as a big-bang mandate.

## 6. Review checklist deltas

`unsafe` without SAFETY comment, `unwrap`/`expect` in production paths,
blocking in interrupt context, priority inversion across RTIC resources,
toolchain drift (lockfile/toolchain diff in review).

## 7. Verification of this skill (Phase 4 gate)

- MISRA Rust status honestly labeled unpublished (§2, §4 preamble).
- Zero unreviewed `unsafe`; panic policy tested, not assumed.
