---
name: axiom-sensor-calibration
title: Sensor Calibration
description: >
  Plans and executes sensor calibration: offset and gain, factory and field
  procedures, two-point calibration, temperature compensation, NVM storage,
  validation and drift tracking without fabricating constants.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [generic-embedded, iot, industrial, automotive, robotics]
platforms: [mcu, mpu, soc, mpsoc]
axiom:
  dotted_name: axiom.generic-embedded.sensor.calibration
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [calibration, offset, gain, nvm, temperature-compensation]
  related_skills: [axiom-sensor-acquisition, axiom-digital-filtering, axiom-sensor-diagnostics, validation]
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [calibration procedure, calibration record, nvm layout]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom Sensor Calibration

## Purpose
Defines calibration methodology for sensors: offset/gain correction, factory vs
field procedures, two-point calibration, temperature compensation, storage in
NVM, validation and drift tracking. Emphasizes evidence and forbids fabricating
constants.

Scope: sensor calibration (generic-embedded). Maturity: experimental. This skill
is original AxiomEmbedded content.

## When to Use
- Commissioning a new sensor or product line.
- Correcting offset, gain or nonlinearity.
- Implementing field recalibration.
- Tracking drift over lifetime.

## When Not to Use
- For acquisition architecture (use axiom-sensor-acquisition).
- For filtering (use axiom-digital-filtering).
- When no reference standard or golden unit is available (record the gap).

## Required Inputs
- Repository path and target file list.
- Sensor datasheet accuracy and temperature coefficient.
- Reference standard or golden unit available for calibration.
- NVM layout and write endurance budget.
- Operating temperature range.

## Optional Inputs
- Existing calibration records.
- Factory calibration data.
- Drift history.

## Prerequisites
- Stable measurement setup and reference.
- NVM driver with wear leveling if needed.
- Temperature chamber or controlled environment for temp comp.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and calibration artifacts.
3. Define calibration model and procedure.
4. Implement calibration capture and computation.
5. Implement NVM storage and validation.
6. Implement temperature compensation.
7. Validate and record evidence.
8. Run checks and record results.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Never fabricate calibration constants; derive from measured reference.
- Store calibration with version, CRC and validity flag.
- Validate calibration on boot; fall back to factory or safe default if invalid.
- Track drift and trigger recalibration thresholds.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-sensor-calibration/`.
- Calibration procedure and records.
- NVM layout documentation.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Calibration validated against reference within declared tolerance.
- Drift tracking demonstrated.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-sensor-calibration`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Fabricated constants -> invalid measurements; always derive from reference.
- Missing CRC -> corrupted calibration applied silently.
- No temperature comp -> drift across operating range.
- Excessive NVM writes -> wear-out.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Calibration Models
- Offset: corrected = raw - offset.
- Gain: corrected = raw * gain.
- Two-point: solve offset and gain from two reference points.
- Polynomial or piecewise for nonlinear sensors; justify order.
- Keep the model minimal; prefer two-point over high-order fits.

## 2. Factory vs Field Calibration
- Factory: controlled environment, reference standard, full temperature range,
  stored as golden calibration.
- Field: user-triggered or scheduled, limited points, updates field overlay
  without overwriting factory baseline.
- Always preserve factory calibration; field calibration is a delta or
  replacement with audit trail.

## 3. Two-Point Procedure
1. Expose sensor to reference low point; record raw.
2. Expose sensor to reference high point; record raw.
3. Compute offset and gain.
4. Validate at a mid point.
5. Store with CRC and validity flag.
6. Reject if residual error exceeds tolerance.

## 4. Temperature Compensation
- Characterize offset/gain vs temperature in a chamber.
- Store a temperature coefficient or lookup table.
- Apply compensation using the sensor's own temperature if available.
- Validate across the operating range; record worst-case residual.

## 5. NVM Storage
- Store calibration struct with version, CRC32 and validity flag.
- Use wear leveling or update counters for frequent writes.
- Provide read/write APIs with typed errors.
- Never write on every sample; write only on calibration events.
- Document memory layout and migration path for version changes.

## 6. Validation
- On boot, read and validate CRC; mark invalid if mismatch.
- Apply factory fallback when field calibration invalid.
- Cross-check against a secondary reference periodically.
- Record calibration date, operator and reference ID.

## 7. Drift Tracking
- Periodically compare sensor output to a reference or redundancy.
- Track trend and set recalibration threshold.
- Log drift events for fleet analysis.
- Do not auto-correct without evidence and review.

## 8. Evidence
- Calibration procedure document.
- Reference standard certificates and IDs.
- Raw and corrected data sets.
- Temperature characterization data.
- NVM read-back verification.
