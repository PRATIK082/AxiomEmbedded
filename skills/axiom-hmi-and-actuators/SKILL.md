---
name: axiom-hmi-and-actuators
title: HMI and Actuators Engineering
description: 'Engineers human-machine interfaces and actuators: keypad matrix scanning
  and debouncing, LCD1602/OLED displays, LEDs, active/passive buzzers, DC/stepper/servo
  motors, encoders, relays, interlocks and e-stop, with electrical and timing constraints
  and verification.

  '
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains:
- all
platforms:
- mcu
- mpu
- soc
axiom:
  dotted_name: axiom.platform.hmi.actuators
  domain: platform
  subdomain: hmi
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags:
  - hmi
  - actuators
  - keypad
  - display
  - motor
  - relay
  - estop
  related_skills:
  - drivers
  - safety
  - axiom-interlock-estop-architecture
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
  - HMI/actuator interface spec
  - safety I/O matrix
  - verification report
  mcp_tools:
  - run_skill
  - validate_skill
  risk_level: high
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
  checklists:
  - checklists/review.yaml
---

# Axiom HMI and Actuators Engineering

## Purpose
Engineers human-machine interfaces and actuators with robust scanning/debouncing, electrical constraints,
safe actuation, and interlock/e-stop awareness. This skill is original AxiomEmbedded content.

Scope: hmi (platform). Maturity: experimental.

## When to Use
- The project needs keypad/display/LED/buzzer/motor/relay/encoder design or verification.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- I/O budget, voltage/current limits, and safety requirements.

## Optional Inputs
- Existing driver code, schematics, timing captures, prior test reports.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded (`drivers`, `safety`, `interlock-estop-architecture`).

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing HMI/actuator artifacts.
3. Select components and interfaces per requirements.
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

## Keypads (matrix scanning and debouncing)
- Use row/column scanning with diodes or strobe to avoid ghosting.
- Debounce with time-based (>= 20 ms typical) or counter-based filters; document threshold.
- Detect press/release edges and auto-repeat policy explicitly.
- Handle stuck-key and all-keys-pressed fault cases.
- Protect inputs with ESD/EMI filtering; verify logic levels.

## Displays
- **LCD1602 (parallel)**: manage RS/RW/E timing; 4-bit mode saves pins; allow init delay.
- **LCD1602 (I2C backpack)**: verify I2C address and expander mapping; reduce bus traffic.
- **OLED (I2C/SPI)**: handle init sequence, charge pump, and refresh rate; avoid burn-in.
- Abstract display API (clear, print, cursor, backlight) independent of transport.
- Test contrast/backlight and viewing angle under target lighting.

## LEDs and buzzers
- Size current-limiting resistors for target brightness and MCU pin limits.
- Use PWM for dimming/brightness control; avoid excessive EMI.
- Active buzzers: simple on/off; passive buzzers: drive with PWM at desired frequency.
- Provide non-blocking beep patterns; keep buzzer current within supply budget.
- Indicate fault states with distinct, documented patterns.

## Motors (DC, stepper, servo)
- **DC**: H-bridge with PWM speed control; enforce current limits and thermal protection.
- **Stepper**: step/dir with microstepping; verify torque/speed and missed-step detection.
- **Servo**: PWM position control; respect update rate and travel limits.
- Add soft-start/stop and stall detection; prevent back-EMF damage with freewheel diodes.
- Never command motion without interlock/enable chain satisfied.

## Encoders
- Use hardware quadrature decoding when available; filter glitches.
- Handle direction, index pulse, and overflow; compute velocity with bounded error.
- Debounce mechanical encoders; verify counts under vibration.

## Relays and power switching
- Respect coil current and flyback suppression; use snubbers for inductive loads.
- Enforce minimum on/off times to reduce wear and arcing.
- Provide status feedback (aux contacts) for critical loads.
- Isolate control from mains/high voltage per safety requirements.

## Safety (interlocks, e-stop)
- Wire e-stop in hardware (NC chain) independent of firmware; firmware monitors, never creates safety.
- Require deliberate restart sequence after stop; prevent auto-restart.
- Implement interlocks as fail-safe (open to stop) and test defeat/shorted-wire cases.
- Map all safety I/O in a safety I/O matrix and trace to risk assessment.
- Cross-reference `interlock-estop-architecture` for topology and categories.

## Electrical and timing constraints
- Verify pin current/voltage limits, total port current, and supply budget.
- Debounce/scan timing must fit within control loop period.
- Avoid blocking I/O in time-critical paths; use DMA/interrupts where appropriate.
- Test EMI/ESD susceptibility and recovery.

## Verification
- Measure scan/debounce timing and actuator response with scope/logic analyzer.
- Test interlock/e-stop wiring faults (open, short, stuck).
- Run motor/relay endurance and thermal tests.
- Validate display readability and buzzer audibility in target environment.
- Record all measurements and pass/fail against requirements.

## Deliverables
- HMI/actuator interface specification and I/O matrix.
- Verification report with measurements and fault-injection results.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-hmi-and-actuators`.
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
- Cross-references: `drivers`, `safety`, `interlock-estop-architecture`.
