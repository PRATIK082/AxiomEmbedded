---
name: embedded-c
description: C17 embedded subset, integer/pointer discipline, startup and linker artifacts. Use when writing C firmware or configuring toolchains.
version: 1.3.0
domains: [all]
platforms: [mcu, bare-metal, rtos]
axiom:
  dotted_name: axiom.legacy.embedded-c
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills: []
  checklists:
  - checklists/embedded-c-checklist.md
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
   isolated behind the HAL (`mcu` S6) with documented confinement.
2. **Integers are explicit.** `stdint.h` types everywhere; no plain `int` in
   interfaces; signed/unsigned mixing is a defect; overflow checked or proven
   impossible at review -- never assumed away.
3. **Pointers are owned.** Single ownership documented per pointer; no pointer
   arithmetic outside buffers with proven bounds; `const` correctness enforced;
   function pointers live in tables reviewed for integrity (safety-relevant
   tables additionally CRC-checked or in protected flash).
4. **No dynamic allocation after init** on constrained targets (heap rules per
   `rtos` S5); where the heap exists, malloc/free pairing is review-checked
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
   (see `mcu` S5); bootloader/application boundaries enforced by hardware,
   not convention.

## 5. Review checklist deltas (on top of `implementation` S5)

Integer conversions, shift widths, volatile misuse, ISR reentrancy, stack-depth
worst case, linker drift (map diff in review), MISRA deviation validity.

## 6. Verification of this skill (Phase 4 gate)

- C17 + MISRA C:2025 cited with version + URL (S2).
- Zero undocumented deviations; map-file evidence per release.



## 7. Embedded C style rules (naming, types, variables, macros, headers, memory, concurrency, errors, documentation)

### 7.1 Interface boundary rule
Application and business modules (`app/`, `module/`) must never call HAL or vendor APIs directly. Only `interface/` and `bsp/` layers may access vendor HAL. Forbidden in `app/` and `module/`: `HAL_GPIO_WritePin`, `HAL_UART_Transmit`, `HAL_SPI_Transmit`, `HAL_I2C_Master_Transmit`.

### 7.2 Naming rules
- **Types**: `typename_t` (e.g. `motor_t`, `uart_config_t`). Forbidden: `Motor`, `PIDStruct`, `UART_CONFIG`.
- **Functions**: `module_action()` lowercase underscore (e.g. `motor_init()`, `motor_set_speed()`). Internal file-scope functions must be `static`.
- **Macros**: `MODULE_DESCRIPTION` uppercase underscore (e.g. `MOTOR_MAX_SPEED_RPM`). Forbidden: `MaxSpeed`, `bufferSize`.

### 7.3 Type rules
Always use `<stdint.h>` fixed-width types. Forbidden: bare `int`, `short`, `long`, `unsigned`. Booleans must use `<stdbool.h>` (`bool`); forbidden substitutes: `u8 flag`, `uint8_t status` as boolean.

### 7.4 Variable rules
- Plain global variables are forbidden. File-private `static` is allowed. Cross-module access must go through interface functions (`motor_get_speed()`), not `extern int speed`.
- Immutable data must be `const`.
- `volatile` only for ISR-shared variables, DMA status, memory-mapped registers. Forbidden on ordinary variables.

### 7.5 Function rules
- Pointer parameters must be null-checked before dereference, returning an error code.
- Callers must check return values; ignored return values are forbidden.

### 7.6 Macro rules
- No magic numbers; all constants are named macros.
- Macro bodies must be fully parenthesized.

### 7.7 Header rules
- Every header must use include guard (`#ifndef`/`#define`/`#endif`) or `#pragma once`.
- Prefer forward declarations over `#include` in headers to minimize dependencies.

### 7.8 Memory rules
- No runtime heap allocation (`malloc`/`calloc`/`realloc`/`free`) in firmware; use static allocation. Prevents fragmentation and unpredictable latency.

### 7.9 Concurrency rules
Shared resources accessed from multiple threads or ISRs must be protected with mutex or critical section.

### 7.10 Error handling rules
Use a single project-wide `error_t` enum (e.g. `ERR_OK`, `ERR_TIMEOUT`, `ERR_BUSY`, `ERR_INVALID_PARAM`, `ERR_NOT_INITIALIZED`, `ERR_OVERFLOW`). Forbidden: magic return values like `return -1`.

### 7.11 Documentation rules
All public interfaces must carry Doxygen-style doc blocks (`@brief`, `@param`, `@return`).

### 7.12 Validation checklist
- [ ] `<stdint.h>` types used; no bare `int`/`short`/`long`/`unsigned`
- [ ] `<stdbool.h>` used for booleans
- [ ] Internal functions declared `static`
- [ ] No unchecked pointer dereference
- [ ] No ignored return values
- [ ] No runtime `malloc`/`free`
- [ ] No magic numbers
- [ ] Macro bodies parenthesized
- [ ] Globals minimized; cross-module access via functions
- [ ] `const` used for immutable data
- [ ] `volatile` only for ISR/DMA/register
- [ ] Naming follows `module_action`, `typename_t`, `MACRO_NAME`
- [ ] Public interfaces have Doxygen blocks
- [ ] No HAL calls in `app/` or `module/`

### 7.13 Auto-fix strategy
When violations are found: report with file/line, explain embedded impact (safety/determinism/portability), provide corrected code, refactor automatically if mechanical. Priority: Safety > Determinism > Maintainability > Readability.

