---
name: axiom-multi-sensor-synchronization
title: Multi-Sensor Synchronization
description: Synchronizes multiple sensors across shared triggers, aligned timestamps,
  clock domains and fusion timing with deterministic sampling and resource arbitration.
  Use when multi sensor synchronization tasks arise in generic-embedded projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains:
- generic-embedded
- iot
- industrial
- automotive
- robotics
platforms:
- mcu
- mpu
- soc
- mpsoc
axiom:
  dotted_name: axiom.generic-embedded.sensor.multi.sensor.synchronization
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags:
  - synchronization
  - multi-sensor
  - fusion
  - trigger
  - clock-domain
  related_skills:
  - axiom-sensor-acquisition
  - axiom-sampling-timestamping
  - axiom-sensor-diagnostics
  - axiom-digital-filtering
  lifecycle:
  - requirements
  - architecture
  - design
  - implementation
  - integration
  - verification
  - validation
  - release
  standards: []
  artifact_types:
  - sync design
  - timing alignment evidence
  mcp_tools:
  - run_skill
  - validate_skill
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
# Axiom Multi-Sensor Synchronization

## Purpose
Synchronizes multiple sensors for coherent data: shared triggers, timestamp
alignment, clock domains, fusion timing, ordering and resource arbitration with
deterministic sampling and evidence.

Scope: multi-sensor synchronization (generic-embedded). Maturity: experimental.
This skill is original AxiomEmbedded content.

## When to Use
- Integrating two or more sensors that must be temporally aligned.
- Designing sensor fusion pipelines.
- Resolving timestamp skew or ordering issues.
- Arbitrating shared buses or triggers.

## When Not to Use
- For single-sensor acquisition (use axiom-sensor-acquisition).
- For sampling details (use axiom-sampling-timestamping).
- For fusion algorithms (record as application work).

## Required Inputs
- Repository path and target file list.
- List of sensors and their rates and latencies.
- Available triggers, timers and clock sources.
- Fusion timing requirements and skew tolerance.

## Optional Inputs
- Timing captures and skew measurements.
- Existing sync design.

## Prerequisites
- Individual sensor drivers and sampling in place.
- Common time base or synchronization mechanism.
- Measurement equipment for skew verification.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and timing artifacts.
3. Define sync architecture (trigger, timestamp alignment).
4. Implement shared trigger and timestamp capture.
5. Implement ordering and arbitration.
6. Validate skew and timing.
7. Run checks and record results.
8. Produce traceability and review evidence.
9. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer hardware triggers over software sync when available.
- Use one time base across all sensors.
- Document skew and its bound as evidence.
- Never assume sensors are synchronized without measurement.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-multi-sensor-synchronization/`.
- Sync design and timing alignment evidence.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Measured skew within declared tolerance.
- Resource arbitration tested.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-multi-sensor-synchronization`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Software-only sync -> unbounded skew.
- Multiple time bases -> misalignment.
- Unarbitrated bus access -> corruption.
- Ignored sensor latency -> fusion errors.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Shared Trigger
- Use a single hardware trigger (timer, GPIO, PWM) to start conversions.
- Distribute trigger with matched delays; account for trace length.
- Verify trigger arrival at each sensor.

## 2. Timestamp Alignment
- Capture timestamps in a common time base at each sensor.
- Compensate for known per-sensor latency (conversion + read time).
- Record skew and apply correction in fusion.

## 3. Clock Domains
- Identify all clock domains (MCU, sensor internal, bus).
- Use a common reference (PPS, GPS, or MCU master clock) when possible.
- Document drift between domains and resync strategy.

## 4. Fusion Timing
- Define the fusion window and maximum allowable skew.
- Buffer samples until all channels for a window are available.
- Handle late or missing samples with defined policy (drop, interpolate, degrade).

## 5. Ordering
- Preserve capture order; timestamp primary sort key.
- Use sequence numbers to detect drops and reordering.
- Document channel ordering in the fusion interface.

## 6. Resource Arbitration
- Arbitrate shared buses (I2C/SPI) with a scheduler or mutex at the bus layer.
- Avoid priority inversion; use bounded waits.
- Document bus utilization and worst-case latency.

## 7. Deterministic Sampling
- Fixed schedule; no dynamic reallocation in runtime path.
- Measure worst-case end-to-end latency.
- Verify under load (all sensors active).

## 8. Evidence
- Trigger and timestamp captures.
- Skew measurements across temperature and load.
- Bus utilization analysis.
- Fusion timing test results.
