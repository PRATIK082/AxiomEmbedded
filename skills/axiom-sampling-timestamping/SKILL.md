---
name: axiom-sampling-timestamping
title: Sampling and Timestamping
description: >
  Selects sampling rates and timer-driven schedules, captures monotonic
  timestamps, manages jitter and ring buffers, and handles overrun for
  deterministic embedded acquisition. Use when sampling timestamping tasks arise
  in generic-embedded projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [generic-embedded, iot, industrial, automotive, robotics]
platforms: [mcu, mpu, soc, mpsoc]

axiom:
  dotted_name: axiom.generic-embedded.sensor.sampling.timestamping
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [sampling, timestamping, timer, jitter, ring-buffer]

  related_skills: [axiom-sensor-acquisition, axiom-multi-sensor-synchronization, axiom-sensor-diagnostics, performance]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [sampling plan, timing evidence]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs:
  - repository path
  - target files
  - objective
  - constraints
  outputs:
  - run report
  - run manifest
  required_tools:
  - validate_skill
  optional_tools:
  - run_skill
---
# Axiom Sampling and Timestamping

## Purpose
Establishes deterministic sampling schedules and trustworthy timestamps for
embedded sensor data: frequency selection, timer-driven triggering, monotonic
clock sources, jitter control, buffering and overrun handling.

Scope: sampling and timestamping (generic-embedded). Maturity: experimental. This
skill is original AxiomEmbedded content.

## When to Use
- Defining or changing a sensor sampling rate.
- Implementing timer-driven acquisition.
- Diagnosing jitter, drift or missed samples.
- Building multi-channel or multi-sensor buffers.

## When Not to Use
- For sensor chip integration (use axiom-sensor-driver-integration).
- For filtering (use axiom-digital-filtering).
- For cross-sensor sync design (use axiom-multi-sensor-synchronization).

## Required Inputs
- Repository path and target file list.
- Required sample rate and jitter bound.
- Available timers and clock sources.
- Buffer size and consumer throughput.
- Platform scheduling (bare-metal/RTOS/Linux).

## Optional Inputs
- Oscilloscope/logic analyzer captures.
- Existing timing measurements.

## Prerequisites
- Timer and clock configuration understood.
- Monotonic time source available (hardware timer counter or RTC).
- Bounded buffer implementation available.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and timing artifacts.
3. Select sample rate and timer.
4. Implement timer-driven sampling with ISR discipline.
5. Implement monotonic timestamp capture.
6. Implement ring buffer with overrun policy.
7. Validate and measure jitter.
8. Run checks and record results.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Sample rate must be justified by Nyquist and application need, not by habit.
- Timestamp at capture time, never at processing time.
- No blocking or allocation in the sampling ISR.
- Overrun must be detected and reported, never silently overwrite without flag.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-sampling-timestamping/`.
- Sampling plan and timing evidence.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Measured jitter within declared bound.
- Overrun detection tested.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-sampling-timestamping`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Timestamp at processing time -> stale or variable timestamps.
- Blocking in ISR -> missed samples and jitter spikes.
- Unbounded buffers -> memory exhaustion.
- Silent overrun -> undetected data loss.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Frequency Selection
- Apply Nyquist: sample at least 2x the highest frequency of interest; add
  margin (typically 5-10x for control loops).
- Match sensor ODR (output data rate) and bus throughput.
- Consider power and CPU budget; do not oversample without reason.
- Document the chosen rate, rationale and margin.

## 2. Timer-Driven Sampling
- Use a hardware timer with a compare/PWM or update interrupt.
- Configure prescaler and period for the target frequency; verify with a scope.
- Keep the ISR minimal: capture timestamp, trigger read or set flag, return.
- Avoid software delays; use one-shot or periodic timer modes consistently.
- On RTOS, prefer a high-priority timer task or ISR + queue.

## 3. Timestamp Sources
- Use a monotonic counter: DWT CYCCNT, SysTick, or a 32/64-bit timer.
- Prefer hardware timer counts converted to microseconds/nanoseconds.
- RTC is for wall-clock only; not for high-resolution sample timing.
- Capture the timestamp as close to the sample event as possible.
- Store timestamps in a fixed unit (e.g. microseconds) with documented epoch.

## 4. Monotonic Timestamps
- Timestamps must never go backwards.
- Handle counter overflow with 64-bit accumulation or documented wrap handling.
- Use a single time base across channels in a system.
- Synchronize software timestamps to hardware capture when possible.

## 5. Jitter
- Jitter sources: ISR latency, bus contention, cache misses, RTOS scheduling.
- Measure with oscilloscope or timer capture; record peak and RMS.
- Reduce by: fixed priority, short ISRs, disabling preemption in critical
  sections, cache locking where available.
- Document the measured jitter bound as evidence.

## 6. Ring Buffer
- Fixed-size circular buffer with head/tail indices.
- Power-of-two size for fast modulo.
- Single producer / single consumer where possible; otherwise protect with
  critical section or lock-free atomics.
- Store sample + timestamp (+ channel id) as a struct.
- Provide peek/count/overflow query APIs.

## 7. Overrun Handling
- Detect when producer overtakes consumer.
- Policy options: drop newest, drop oldest, or block producer (bounded wait).
- Always set an overrun flag and counter; never silently lose data.
- Report overrun to diagnostics; escalate if persistent.
- Size buffers from worst-case consumer latency plus margin.

## 8. Multi-Channel Sync
- Sample all channels on a common trigger when hardware allows.
- Timestamp per channel with the shared time base.
- Document channel ordering and skew.
- See axiom-multi-sensor-synchronization for cross-sensor alignment.

## 9. Deterministic Intervals
- Avoid blocking calls in the sampling path.
- Pre-allocate buffers; no malloc in runtime path.
- Keep conversion and filtering out of the ISR (defer to task).
- Verify worst-case execution time of ISR and task.

## 10. Evidence
- Timer configuration and period calculations.
- Scope captures of sample interval and jitter.
- Overrun injection test results.
- Buffer sizing rationale.
