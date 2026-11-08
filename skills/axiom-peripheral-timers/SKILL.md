---
name: axiom-peripheral-timers
title: Peripheral Timers, PWM and RTC Engineering
description: >
  Engineers MCU timers, counters, PWM, capture/compare and RTC subsystems: modes, prescalers,
  deterministic intervals, overflow handling, watchdog interaction, interrupt latency,
  calibration, and platform differences (AVR/ESP32/Zephyr), verified on hardware.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, bare-metal, rtos]
axiom:
  dotted_name: axiom.platform.peripheral.timers
  domain: platform
  subdomain: timers
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [timers, pwm, rtc, counters]
  related_skills:
  - drivers
  - mcu
  - performance
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [timer configuration record, timing verification report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists:
  - checklists/review.yaml
---

# Axiom Peripheral Timers, PWM and RTC Engineering

## Purpose
Engineers timer, counter, PWM and RTC subsystems with deterministic intervals, bounded interrupt latency,
safe overflow handling, and hardware-verified timing. This skill is original AxiomEmbedded content.

Scope: timers (platform). Maturity: experimental.

## When to Use
- The project needs timer/counter/PWM/RTC design, configuration, or timing verification.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- MCU/board clock tree, timer peripheral documentation, and required timing budgets.

## Optional Inputs
- Existing timer drivers, oscilloscope/logic-analyzer captures, prior run manifests.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded (`mcu`, `drivers`, `performance`).

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing timer artifacts.
3. Select timer mode and clock source per requirement.
4. Generate or modify artifacts (dry-run first).
5. Validate structurally and semantically (scripts/ + checklists/).
6. Run applicable checks; record results.
7. Produce traceability and review evidence.
8. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer explicit configuration over invented defaults; flag every assumption.
- Safety/security-relevant outputs require human review (review_required: true).

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Timer modes and selection
- **One-shot**: single delayed event; ensure re-arming is explicit and race-free.
- **Periodic**: fixed cadence; use compare-match or auto-reload with overflow handling.
- **Input capture**: timestamp edges for frequency/pulse-width measurement; guard against missed edges at high rate.
- **Output compare**: schedule future actions; account for compare-register update latency.
- **PWM**: edge- or center-aligned; choose frequency vs duty resolution tradeoff.
- **Quadrature/encoder**: use hardware encoder interface when available; software decoding only with proven jitter bounds.
- **RTC/calendar**: use dedicated low-power timer; keep application timers separate from wall-clock time.

## Prescalers and clocking
- Derive timer clock from a known, stable source; document the clock tree and any bus dividers.
- Compute prescaler as `timer_clock / (desired_tick_rate)` and verify integer divisibility; flag non-integer ratios.
- Prefer 32-bit (or chained 16-bit) counters for long intervals; use 16-bit only with explicit overflow handling.
- Recompute all timing constants when the system clock changes (e.g., low-power modes, clock switching).
- Avoid changing prescaler at runtime unless the timer is stopped and re-synchronized.

## Capture/compare and PWM
- For PWM, document frequency, duty resolution (bits), alignment, and update policy (immediate vs next period).
- Use shadow/buffered compare registers to avoid glitches; update only at period boundary.
- Add dead-time insertion for complementary outputs driving H-bridges; verify no shoot-through.
- For capture, filter input glitches in hardware when available; otherwise validate pulse width plausibility.
- Measure actual PWM frequency/duty with a logic analyzer; do not trust configured values alone.

## Watchdog interaction
- Feed watchdogs from a defined, monitored execution point; never from an ISR that can run while the main loop is stuck.
- For windowed watchdogs, keep feed timing inside the valid window; document min/max feed intervals.
- Separate watchdog clock from the timer under test where possible; reset reasons must be logged.
- Test watchdog recovery and confirm safe-state entry on timeout.

## Interrupt latency and deterministic intervals
- Bound ISR execution time (target < 10 us for high-rate timers unless justified).
- Set priorities to protect time-critical timers from lower-priority ISRs and task preemption.
- Measure jitter with a scope/logic analyzer over >= 10^5 cycles; report min/max/mean.
- Avoid dynamic allocation and unbounded loops in timer ISRs.
- Use deferred processing (task/DPC) for heavy work triggered by timer events.

## Overflow and timebase handling
- Detect and count overflows; expose a 64-bit (or extended) monotonic timebase to consumers.
- Handle wrap-around in comparisons using unsigned arithmetic or explicit epoch counters.
- Timestamp events with the extended counter, not raw 16/32-bit values.
- Test overflow boundaries (MAX-1, MAX, 0, 1) in unit tests.

## RTC timekeeping and calibration
- Keep RTC on a dedicated backup domain with independent power; validate retention across reset/power cycle.
- Store epoch and handle leap years/days; document timezone/UTC policy.
- Calibrate against a reference (GPS PPS, TCXO, or network time) and record drift (ppm).
- Apply temperature compensation if the oscillator requires it; document calibration intervals.
- Verify RTC accuracy over the required temperature and voltage range.

## Platform differences
- **AVR**: 8-bit timers with limited prescalers; use CTC mode for precise intervals; watch for 16-bit register access atomicity.
- **ESP32**: use LEDC for PWM, MCPWM for motor control, RMT for precise pulses; APB clock changes with CPU frequency.
- **Zephyr**: use counter API and PWM driver; configure via devicetree; verify board-specific clock sources.
- Abstract platform details behind a driver interface; keep timing math platform-neutral.

## Verification
- Measure timer/PWM frequency and duty with oscilloscope or logic analyzer.
- Capture jitter histogram and compare against budget.
- Run long-duration drift tests for RTC; record ppm error.
- Inject missed-edge/overflow scenarios and confirm safe handling.
- Verify behavior across reset, low-power, and clock-switch transitions.

## Deliverables
- Timer configuration record (mode, clock, prescaler, period, duty, ISR budget).
- Timing verification report with measurements and pass/fail against budget.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-peripheral-timers`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `drivers`, `mcu`, `performance`.
