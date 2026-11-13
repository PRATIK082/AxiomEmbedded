---
name: axiom-digital-filtering
title: Digital Filtering for Sensor Data
description: >
  Applies digital filters to sensor data: moving average, IIR low-pass, FIR,
  median, outlier rejection and saturation, with fixed-point and latency
  considerations and verification on known signals. Use when digital filtering
  tasks arise in generic-embedded projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [generic-embedded, iot, industrial, automotive, robotics]
platforms: [mcu, mpu, soc, mpsoc]

axiom:
  dotted_name: axiom.generic-embedded.sensor.digital.filtering
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [filtering, iir, fir, median, fixed-point]

  related_skills: [axiom-sensor-acquisition, axiom-sensor-calibration, axiom-sensor-diagnostics, unit-test]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [filter design note, filter test vectors]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Digital Filtering for Sensor Data

## Purpose
Provides digital filtering techniques for embedded sensor streams: moving
average, IIR, FIR, median, outlier rejection and saturation, with attention to
fixed-point arithmetic, latency vs noise tradeoffs and deterministic execution.

Scope: digital filtering (generic-embedded). Maturity: experimental. This skill
is original AxiomEmbedded content.

## When to Use
- Reducing noise in sensor measurements.
- Rejecting spikes or outliers.
- Implementing anti-aliasing before downsampling.
- Meeting a latency vs noise tradeoff.

## When Not to Use
- For acquisition architecture (use axiom-sensor-acquisition).
- For calibration (use axiom-sensor-calibration).
- For application-specific control tuning (record as application work).

## Required Inputs
- Repository path and target file list.
- Signal characteristics: bandwidth, noise, sample rate.
- Latency budget and acceptable group delay.
- Numeric format (float, fixed-point Q) and CPU budget.

## Optional Inputs
- Recorded signal captures for verification.
- Reference filter specifications.

## Prerequisites
- Sampling and timestamping in place.
- Fixed-point or float math library available.
- Test vectors for verification.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and signal artifacts.
3. Select filter type and parameters.
4. Implement filter with deterministic execution time.
5. Verify with known signals.
6. Run checks and record results.
7. Produce traceability and review evidence.
8. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Justify filter order and cutoff from signal bandwidth and noise.
- Keep execution time bounded and measured.
- Prefer fixed-point on MCU when deterministic timing matters.
- Never claim optimal filtering without measured evidence.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-digital-filtering/`.
- Filter design note and test vectors.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Filter verified on known signals within tolerance.
- Worst-case execution time measured.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-digital-filtering`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Wrong cutoff -> attenuates signal or leaves noise.
- Fixed-point overflow -> clipped or wrong output.
- Unbounded execution time -> jitter in control loop.
- Phase lag ignored -> instability in feedback.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Moving Average
- Simplest smoothing; cutoff ~ fs / (2*N).
- Use circular buffer of last N samples.
- O(N) per sample unless optimized; consider exponential smoothing for O(1).
- Phase lag = (N-1)/2 samples.

## 2. IIR Low-Pass
- First-order: y = alpha*x + (1-alpha)*y_prev.
- Choose alpha from cutoff: alpha = 1 - exp(-2*pi*fc/fs).
- Low memory and O(1) cost; nonlinear phase.
- Watch for coefficient precision in fixed-point.

## 3. FIR
- Linear phase possible with symmetric coefficients.
- Higher cost (O(N)) but stable and predictable.
- Design with windowed sinc or Parks-McClellan; store coefficients as const.
- Use CMSIS-DSP or hand-rolled; verify numerical precision.

## 4. Median Filter
- Effective against impulse (salt-and-pepper) noise.
- Sort small window (3, 5, 7); O(N log N) or insertion sort.
- Preserves edges better than averaging.
- Not suitable for all signal types; validate.

## 5. Outlier Rejection
- Reject samples outside expected range or beyond N sigma from recent mean.
- Use Hampel identifier or threshold on derivative.
- Mark rejected samples; do not silently interpolate without policy.
- Combine with a smoothing filter after rejection.

## 6. Saturation and Clamping
- Clamp outputs to physical range to prevent downstream damage.
- Apply before and after filtering as appropriate.
- Log saturation events for diagnostics.

## 7. Fixed-Point Considerations
- Choose Q format (e.g. Q15, Q31) with headroom for accumulation.
- Use saturating arithmetic; check overflow.
- Document scaling of coefficients and signals.
- Verify against float reference in tests.

## 8. Latency vs Noise Tradeoff
- More filtering -> less noise but more delay and phase lag.
- Match group delay to control loop timing budget.
- Measure and document step response and settling time.

## 9. Deterministic Execution Time
- Fixed iteration counts; no data-dependent loops where possible.
- Measure worst-case execution time on target.
- Avoid dynamic allocation in filter path.

## 10. Verification
- Test with known signals: step, impulse, sine, noise.
- Compare output to reference (float or golden).
- Measure frequency response if needed.
- Include overflow and boundary tests.
