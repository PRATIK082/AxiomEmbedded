# Bare-Metal skill

Single-core, no-OS firmware on MCU targets: reset-to-main structure, interrupt
design, super-loop and static-schedule architectures, and bringing a board from
first power-on to a deterministic main loop — the foundation under `mcu`,
`drivers`, and `bootloader`.

## 1. Purpose and scope

**Purpose.** Deliver deterministic firmware without an OS: bounded interrupt
latency, no hidden allocation, and a main-loop architecture whose timing is
measured, not assumed.

**In scope.** Startup code (Reset_Handler, vector table, `.data`/`.bss` init),
clock and peripheral init order, NVIC/interrupt design, super-loop and
time-triggered static schedules, sleep/idle power discipline, and linker-map
evidence of fit.

**Non-goals.** RTOS scheduling (see `rtos`), Linux userspace (see
`embedded-linux`). This skill ends where an RTOS or OS takes over — and
documents that handoff.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | Arm Cortex-M exception model | ARMv6-M/ARMv7-M/ARMv8-M architecture reference | Exception entry/return, NVIC priority grouping, fault handlers | `https://developer.arm.com/documentation/100235/latest/` |
| 2 | MISRA C | MISRA C:2025 (current); C:2023 baseline | Interrupt-safe subset, no recursion, documented deviations | `https://misra.org.uk/` |
| 3 | C17 | ISO/IEC 9899:2018 | Language baseline for `embedded-c` construction rules | `https://www.iso.org/standard/74528.html` |

## 3. Startup and init order

1. **Reset path is code, not magic.** `Reset_Handler` copies `.data`, zeroes
   `.bss`, configures clocks, then calls `SystemInit` and `main`. Each step is
   reviewed; the vector table is verified against the reference manual
   (position, handlers, reserved slots).
2. **Clock before peripherals.** System clock tree configured and measured
   first; peripheral init order follows dependencies (power → clock → GPIO →
   bus → device). Every init function returns status; `main` halts visibly on
   init failure — never proceeds half-initialized.
3. **Fault handlers that speak.** HardFault/MemManage/BusFault/UsageFault
   capture stacked registers, fault status registers, and a breadcrumb trail
   into retained RAM or backup registers before reset. A fault handler that
   just loops silently is a defect.

## 4. Interrupt discipline

1. **Short ISRs, deferred work.** ISRs flag or enqueue; processing happens in
   the main loop. Maximum ISR duration budgeted and measured; priority grouping
   configured so a fault-class exception always preempts peripheral IRQs.
2. **Shared data protocol.** `volatile` + critical sections (or LDREX/STREX
   where available) for every main/ISR shared variable; multi-byte values never
   read torn. Race review is part of every driver review (see `drivers`).
3. **Latency budget.** Worst-case interrupt latency measured with a GPIO toggle
   under full load; the number goes in the evidence, not the engineer's memory.

## 5. Main-loop architectures

| Pattern | Use when | Timing proof |
|---------|----------|--------------|
| Super-loop | Tasks tolerant to jitter, single rate | WCET per task measured; loop period bounded |
| Time-triggered static schedule | Mixed rates, mild determinism needs | Schedule table reviewed; overrun detection with safe action |
| Foreground/background | Fast ISR + slow loop | ISR budget + loop WCET; shared-data audit |

Sleep (`WFI`) in idle with a wake-accounting: every wake source named, spurious
wakes investigated, never polled away.

## 6. Release gates (blocking)

1. Startup path reviewed; vector table verified against the manual.
2. Init order documented; failures halt visibly, never half-run.
3. ISR durations and worst-case latency measured and recorded.
4. Shared main/ISR data audited for races.
5. Linker map proves fit with margin; no heap use after init.
6. MISRA/static-analysis clean with deviations documented (`implementation` §4).

## 7. Verification of this skill (Phase 4 gate)

- Timing claims are measured on target (§4.3, §5), never estimated.
- Fault handlers produce diagnostics (§3.3), never silent loops.
