---
name: axiom-sensor-diagnostics
title: Sensor Diagnostics
description: >
  Detects sensor faults (stuck-at, out-of-range, timeout, CRC error,
  communication loss), supports degraded mode and watchdogs, and provides
  fault-injection testing and evidence. Use when sensor diagnostics tasks arise
  in generic-embedded projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [generic-embedded, iot, industrial, automotive, robotics]
platforms: [mcu, mpu, soc, mpsoc]

axiom:
  dotted_name: axiom.generic-embedded.sensor.diagnostics
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [diagnostics, fault-detection, degraded-mode, watchdog]

  related_skills: [axiom-sensor-acquisition, axiom-sensor-driver-integration, axiom-sampling-timestamping, axiom-sensor-calibration, axiom-digital-filtering, axiom-multi-sensor-synchronization, validation, fault-injection]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [diagnostics design, fault injection report]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Sensor Diagnostics

## Purpose
Detects and manages sensor faults: stuck-at, out-of-range, timeout, CRC error
and communication loss. Defines degraded modes, watchdogs, reporting and
fault-injection testing with evidence.

Scope: sensor diagnostics (generic-embedded). Maturity: experimental. This skill
is original AxiomEmbedded content.

## When to Use
- Adding fault detection to a sensor path.
- Designing degraded operation for sensor failure.
- Building diagnostic reporting and logging.
- Planning fault-injection campaigns.

## When Not to Use
- For sensor integration (use axiom-sensor-driver-integration).
- For calibration (use axiom-sensor-calibration).
- For safety certification claims (record as safety work).

## Required Inputs
- Repository path and target file list.
- Sensor operating ranges and expected behavior.
- Fault definitions and severity levels.
- Degraded mode requirements.
- Reporting channel (logs, telemetry, DTC).

## Optional Inputs
- Existing diagnostic frameworks.
- Fault trees or FMEA.

## Prerequisites
- Acquisition and driver layers in place.
- Reporting/logging infrastructure.
- Fault injection harness.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and diagnostic artifacts.
3. Define fault types and detection rules.
4. Implement detection and degraded mode.
5. Implement reporting and watchdog.
6. Implement fault injection tests.
7. Validate and record evidence.
8. Run checks and record results.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Every fault must have a defined detection rule and severity.
- Degraded mode must be safe and documented.
- Fault injection must be repeatable and evidenced.
- Never claim safety compliance from diagnostics alone.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-sensor-diagnostics/`.
- Diagnostics design and fault injection report.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Fault injection tests cover all defined faults.
- Degraded mode verified.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-sensor-diagnostics`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing fault coverage -> latent failures.
- No degraded mode -> unsafe shutdown.
- Unrepeatable injection -> unverified diagnostics.
- Alert fatigue -> ignored faults.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Fault Detection
- Stuck-at: detect constant value over N samples.
- Out-of-range: compare against min/max physical limits.
- Timeout: no new sample within expected interval.
- CRC error: checksum mismatch on read.
- Communication loss: bus transaction failures or device not present.
- Implausibility: rate-of-change or cross-sensor inconsistency.

## 2. Watchdog for Sensor
- Arm a watchdog per sensor with timeout = expected period + margin.
- Kick on valid sample; expire triggers fault handling.
- Distinguish soft (retry) vs hard (degrade) expiry.

## 3. Degraded Mode
- Define safe behavior when a sensor fails: hold last valid, use redundant,
  reduce functionality, or safe shutdown.
- Document transition criteria and recovery.
- Ensure degraded mode is tested, not just designed.

## 4. Reporting
- Log faults with timestamp, sensor id, fault type, severity.
- Expose status to telemetry/health endpoint.
- Map to DTCs where applicable.
- Avoid flooding; rate-limit repeated faults.

## 5. Fault Injection Testing
- Inject faults via mock bus: NACK, timeout, short read, CRC fail, stuck value.
- Verify detection latency and correct classification.
- Verify degraded mode activation and recovery.
- Record injection scripts and results as evidence.

## 6. Evidence
- Fault definitions and detection rules.
- Fault injection test results.
- Degraded mode verification.
- Timing of detection vs requirement.
- Review of diagnostic coverage.
