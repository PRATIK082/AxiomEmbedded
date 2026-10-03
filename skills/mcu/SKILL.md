---
name: mcu
description: MCU firmware engineering - core selection, startup, MPU/TrustZone, HAL, RTOS choice. Use for bare-metal or RTOS firmware on Cortex-M/RISC-V.
version: 1.2.0
domains: [generic-embedded, automotive, industrial, iot, robotics]
platforms: [mcu, bare-metal, rtos]
---

# mcu — Microcontroller firmware capability (template skill)

Reusable AxiomEmbedded capability for microcontroller selection, bring-up,
bare-metal/RTOS firmware, drivers, and verification.

> Template status: this skill is the Phase 3 reference implementation.
> Replicate its structure for `rtos`, `autosar`, `safety`, `embedded-linux`,
> `edge-ai`, `robotics` (see `docs/adr/0001-mcu-template.md`).

## Objectives

- Select an MCU (core, memory, peripherals, power, security) against system requirements.
- Bring up clock tree, power domains, startup code, linker layout, and debug access.
- Implement portable drivers (GPIO, UART/SPI/I2C, timers, ADC/DAC, DMA, watchdog).
- Integrate bare-metal super-loop or RTOS (FreeRTOS 202604 LTS / Zephyr LTS).
- Verify with unit, integration, and hardware-in-the-loop tests at the coverage level the ASIL/DAL demands.

## Prerequisites

- System requirements with allocated MCU constraints (flash/RAM/MIPS/power/cost).
- Toolchain: `gcc-arm-none-eabi` or `clang` with `--target=arm-none-eabi`; CMake >= 3.20.
- Debug probe (SWD/JTAG) and a board definition (custom or 1000+ Zephyr-supported boards).
- Domain overlay loaded when applicable: `domains/automotive/`, `domains/aerospace/`, `domains/generic-embedded/`.

## Outcomes

- `requirements/mcu-requirements.md` tracing SYS-xxx to MCU-xxx constraints.
- `architecture/mcu-architecture.md`: core choice rationale, memory map, clock tree, power modes.
- `src/` + `headers/` with Doxygen public APIs, MISRA C:2025 clean.
- `test/` with host unit tests, on-target integration tests, and HIL plan.
- `build/` CMake project, zero warnings with `-Wall -Wextra -Werror` on gcc and clang.
- `evidence/` linking every claim to a standard clause and a test result.

## Time estimate

- Selection + architecture: 2–3 days. Bring-up + drivers: 3–5 days. Verification: 3–5 days.

## Resources

- Arm Cortex-M comparison table (cores M0–M7, TrustZone, MPU regions, DSP/FPU):
  `https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Cortex-A%20R%20M%20datasheets/Arm%20Cortex-M%20Comparison%20Table_v3.pdf`
- MISRA C:2025 (latest; 2023 baseline consolidates MISRA C:2012 + amendments):
  `https://misra.org.uk/misra-c`
- MISRA C:2023 Addendum 3 (CERT C coverage, Jan 2025).
- FreeRTOS 202604 LTS (kernel 11.3.0, MPU support, MQTT v5.0, supported to 2028-04-30):
  `https://www.freertos.org/Community/Blogs/2026/freertos-202604-lts-now-available`
- Zephyr LTS (2+ year support, 1000+ boards): `https://docs.zephyrproject.org/latest/index.html`
- LLVM/Clang CMake 3.20.0 minimum baseline:
  `https://github.com/llvm/llvm-project/blob/main/clang/CMakeLists.txt`

## Core selection guide

| Class | Cores | Use when |
| --- | --- | --- |
| Cost/power | M0/M0+/M23 | Sensors, simple control; M23 adds TrustZone + 16 MPU regions |
| Balanced | M3/M4 | M4 adds DSP + optional single-precision FPU (motor control, audio) |
| Secure/connected | M33/M35P | TrustZone, 16 MPU regions, coprocessor interface (STM32WBA-class BLE) |
| Performance/AI | M55/M7 | Helium vector ext. (M55) or double-precision FPU + caches (M7) |

## Memory protection and security

- Enable the MPU from day one: privileged/unprivileged separation, peripheral
  guard regions, stack-overflow guards. Reserve application MPU regions
  (FreeRTOS 202604 LTS claims fewer regions, leaving room for app use).
- Use TrustZone (M23/M33/M35P/M55) to isolate secure boot, keys, and firmware
  update from application firmware. Document the SAU/IDAU partition.
- Map claims to `rules/security.yaml` and the active domain overlay
  (automotive: ISO 26262 ASIL; aerospace: DO-178C DAL; see `profiles/skill-update-profile.yaml`).

## Startup, linker, and clock

- Provide: vector table with weak default handlers, `Reset_Handler` (copy `.data`,
  zero `.bss`, init clocks, call `main`), linker script with FLASH/RAM/partition
  regions, and a clock-tree diagram in `architecture/`.
- Gate every peripheral clock; verify sleep/deep-sleep current against the datasheet.
- Keep startup files under review: they are safety-relevant in every domain overlay.

## Drivers and HAL

- One driver per peripheral: `init`, `deinit`, `ioctl/config`, explicit error codes —
  no implicit global state (`rules/baseline.yaml`: no-implicit-state, explicit-error-handling).
- Prefer DMA + interrupts over polling; bound every ISR (max complexity 15,
  deterministic init, bounded resource use).
- Doxygen every public header; MISRA C:2025 mandatory/required rules clean or
  formally deviated with rationale in `evidence/`.

## Build

- `cmake_minimum_required(VERSION 3.20)`; presets for `debug`, `release`, `hil`.
- Flags: `-Wall -Wextra -Werror` on gcc and clang; `--target=` triples for
  `arm`, `riscv`, `mips` where the project requires them.
- Static analysis in CI: MISRA checker + `rules/c.yaml` + `rules/embedded-baseline.yaml`.

## RTOS choice

- Bare-metal: super-loop or event-driven, only when timing analysis proves sufficiency.
- FreeRTOS 202604 LTS: kernel 11.3.0, MPU support, 2-year LTS to 2028-04-30.
- Zephyr LTS: pick when POSIX subsets, Devicetree, or 1000+ board support pay off.
- Record the decision and its safety impact in `docs/adr/` (this skill: ADR-0001).

## Test strategy

- Host unit tests for logic (mock registers); on-target integration for timing/peripherals.
- Coverage targets from `configs/skill-update.yaml`: ASIL A/DAL D 100% statement+branch;
  ASIL B/DAL C adds recommended MC/DC; ASIL C-D/DAL A-B requires MC/DC.
- HIL: power measurement, fault injection (`skills/fault-injection/`), watchdog and
  brown-out recovery proven on hardware.

## Traceability

- `traceability-matrix.schema.json`: every SYS-xxx → SW-xxx → `src/` file → `test/` case → evidence id.
- No orphan code, no orphan tests. `scripts/verify_skill.py --skill mcu` enforces presence.

## Compliance mapping (via domain overlays, not duplication)

- Automotive: ISO 26262:2018 Parts 1–10 (ASIL A–D); Edition 3 in DIS — track, do not cite as published.
- Aerospace/defense: DO-178C core + DO-330/331/332/333 as technique requires; DAL A–E.
- Industrial/medical/rail: IEC 61508 SIL via `domains/` overlays; never claim
  certification from this heuristic skill — produce audit-ready evidence only.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill mcu` → PASS.
2. CMake configure + build, gcc and clang, zero warnings.
3. Unit + integration tests green at the required coverage.
4. MISRA C:2025 scan: zero mandatory/required violations or deviated with rationale.
5. Traceability matrix complete; standards cited with number + version + clause + URL.
6. Safety/security deltas flagged for human review before PR.

Load task-specific domain/platform/rule overlays before execution.
