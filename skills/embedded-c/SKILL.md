---
name: embedded-c
description: C17 embedded subset, integer/pointer discipline, startup and linker artifacts. Use when writing C firmware or configuring toolchains.
version: 1.2.0
domains: [all]
platforms: [mcu, bare-metal, rtos]
---

# Embedded-C skill

Idiomatic, safe, portable C for constrained targets: language subset,
memory discipline, startup and linker control, peripheral access patterns,
and the verification story that makes C defensible at ASIL D.

## 1. Purpose and scope

**Purpose.** Write C that is predictable on small targets and clean under
MISRA C:2025 with zero deviations-by-default.

**In scope.** C17 language subset, memory and pointer discipline, volatile and
atomic usage, startup code and linker scripts, fixed-point and integer safety,
portability across gcc/clang/arm/riscv, and C-specific review checklists.

**Non-goals.** C++ features (see `embedded-cpp`), OS-level programming (see
`embedded-linux`, `rtos`). Assumes the `implementation` construction rules and
`mcu` startup/linker foundations.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO C17 | ISO/IEC 9899:2018 | Language baseline; no K&R, no implicit ints | `https://www.iso.org/standard/74528.html` |
| 2 | MISRA C | MISRA C:2025 (current); C:2023 baseline | Mandatory/required/advisory safety rules | `https://misra.org.uk/` |
| 3 | CERT C | Current | Secure-coding rules, MISRA Addendum 3 map (Jan 2025) | `https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard` |

## 3. Language subset rules

1. **C17 only.** No GNU extensions in portable code; target-specific code is
   isolated behind the HAL (`mcu` §6) with documented confinement.
2. **Integers are explicit.** `stdint.h` types everywhere; no plain `int` in
   interfaces; signed/unsigned mixing is a defect; overflow checked or proven
   impossible at review — never assumed away.
3. **Pointers are owned.** Single ownership documented per pointer; no pointer
   arithmetic outside buffers with proven bounds; `const` correctness enforced;
   function pointers live in tables reviewed for integrity (safety-relevant
   tables additionally CRC-checked or in protected flash).
4. **No dynamic allocation after init** on constrained targets (heap rules per
   `rtos` §5); where the heap exists, malloc/free pairing is review-checked
   and allocation failure paths are tested.
5. **`volatile` means hardware.** Only for MMIO and ISR-shared flags, always
   with barriers or atomics (`stdatomic.h` C11+) where ordering matters;
   `volatile` is not a synchronization primitive.

## 4. Startup, linker, and memory map

1. **Startup code reviewed like product code.** Reset handler, `.data` copy,
   `.bss` zeroing, stack pointer init, and `SystemInit` clock setup are
   checked against the reference manual and covered by a boot self-test.
2. **Linker script is a design artifact.** Regions, section placement,
   alignment, stack/heap sizes, and MPU alignment reviewed and versioned;
   the map file is build evidence (size report per release).
3. **Memory protection aligned.** Safety-critical data in MPU-guarded regions
   (see `mcu` §5); bootloader/application boundaries enforced by hardware,
   not convention.

## 5. Review checklist deltas (on top of `implementation` §5)

Integer conversions, shift widths, volatile misuse, ISR reentrancy, stack-depth
worst case, linker drift (map diff in review), MISRA deviation validity.

## 6. Verification of this skill (Phase 4 gate)

- C17 + MISRA C:2025 cited with version + URL (§2).
- Zero undocumented deviations; map-file evidence per release.
