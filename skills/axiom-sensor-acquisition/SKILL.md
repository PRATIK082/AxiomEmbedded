---
name: axiom-sensor-acquisition
title: Sensor Data Acquisition
description: 'Scope and methodology for acquiring sensor data in embedded systems:
  interface selection, sampling, conversion, timestamping, buffering and publication
  with typed errors and evidence.

  '
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
  dotted_name: axiom.generic-embedded.sensor.acquisition
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags:
  - sensor
  - acquisition
  - sampling
  - timestamping
  related_skills:
  - axiom-sensor-driver-integration
  - axiom-sampling-timestamping
  - axiom-sensor-calibration
  - axiom-digital-filtering
  - axiom-sensor-diagnostics
  - axiom-multi-sensor-synchronization
  - drivers
  - unit-test
  - validation
  - performance
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
  - sensor acquisition design note
  - acquisition evidence bundle
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

# Axiom Sensor Data Acquisition

## Purpose
Defines the scope, architecture and methodology for acquiring data from physical
sensors in embedded systems. Covers interface selection, sampling strategy,
signal conversion, timestamping, buffering, publication, error handling and
evidence. This skill is the parent of the sensor sub-skills and sets the shared
vocabulary and contracts they build on.

Scope: sensor acquisition (generic-embedded). Maturity: experimental. This skill
is original AxiomEmbedded content.

## When to Use
- A new sensor is being added to a product or platform.
- An existing acquisition path is being reworked for determinism, throughput or
  accuracy.
- A multi-sensor system needs a common acquisition contract.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety or security certification review.
- When the required hardware information is absent (record the gap instead of
  inventing data).
- For pure signal-processing work with no hardware interface (use
  axiom-digital-filtering).
- For calibration-only tasks (use axiom-sensor-calibration).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Sensor datasheet and reference manual identifiers.
- Interface type (I2C, SPI, UART, 1-Wire, analog, etc.), supply voltage and
  logic levels.
- Required sampling rate, resolution, accuracy and latency budget.
- Platform (bare-metal, RTOS, Linux) and available peripherals (DMA, timers).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.
- Logic analyzer or scope captures of the bus.
- Factory calibration data and NVM layout.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.
- Hardware abstraction layer (HAL/BSP) available for the target bus.
- A mockable register backend for host-side testing.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and existing acquisition artifacts.
3. Collect and record the sensor hardware information.
4. Select architecture (polling, interrupt, DMA) and buffering strategy.
5. Define the typed acquisition context and error enum.
6. Implement init, identify, configure, read, convert, timestamp, publish.
7. Validate structurally and semantically (scripts/ + checklists/).
8. Run applicable checks and record results.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer explicit configuration over invented defaults; flag every assumption.
- Safety/security-relevant outputs require human review (review_required: true).
- Never fabricate calibration constants, timing budgets or accuracy figures.
- One acquisition context per sensor instance; no hidden global state.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-sensor-acquisition/`.
- Sensor acquisition design note.
- Acquisition evidence bundle (timing captures, test results).

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Acquisition path meets the declared sampling rate, latency and accuracy budget.
- Host unit tests with mock registers green.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-sensor-acquisition`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.
- No data on the bus -> check power, wiring, address and init order.
- Wrong values -> check conversion formula, endianness and units.
- Drift over time -> check clock source, temperature and calibration.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Scope and Purpose
Sensor data acquisition is the end-to-end path from a physical quantity to a
timestamped, validated, published measurement. It spans the sensor, the bus,
the driver, the conversion and scaling, the timestamp source, the buffer and
the consumer contract. Keeping this scope explicit prevents acquisition logic
from leaking into application policy.

## 2. Required Hardware Information
Record before implementation:
- Interface type and bus speed (I2C fast mode, SPI clock, UART baud).
- Supply voltage and logic levels; 3.3 V vs 5 V compatibility.
- Sampling rate (Hz) and required jitter bound.
- Resolution (bits) and effective noise-free resolution.
- Accuracy, offset, gain and temperature coefficient from the datasheet.
- Startup, wake and conversion times.
- Maximum bus load (capacitance, number of devices, pull-up values).

## 3. Architecture Considerations
Choose the trigger model deliberately:
- Polling: simplest, deterministic scheduling, wastes CPU, fine for slow sensors.
- Interrupt (data-ready): event-driven, lower latency, requires ISR discipline.
- DMA: highest throughput, complex ownership and cache discipline.
- Hybrid: interrupt to start, DMA to move, CPU to process.
Document ownership at every handoff (CPU vs DMA vs ISR) and the buffer scheme
(single, double, ring). Define who publishes and who consumes.

## 4. Implementation Methodology
Follow this order for every sensor:
1. Init: clock, reset, pin mux, bus init.
2. Identify: read WHO_AM_I / device ID and verify.
3. Configure: sampling rate, range, filters, interrupts via registers.
4. Read: burst or single register read with CRC/checksum when available.
5. Convert: raw to engineering units using documented scale factors.
6. Timestamp: capture a monotonic timestamp at sample time, not at processing time.
7. Publish: push to a bounded buffer or queue with overflow policy.

## 5. Hardware Constraints
- Respect supply and logic voltage limits; never exceed absolute maximums.
- Derive bus timing (I2C clock stretch, SPI mode, setup/hold) from the datasheet.
- Account for bus loading and pull-up resistor values.
- Honor startup and wake times before the first valid read.
- Keep conversion and bus traffic within the declared latency budget.

## 6. Platform Considerations
- Bare-metal: super-loop or timer ISR; avoid blocking; bounded buffers.
- RTOS: timer-driven task or ISR + queue; protect shared state with critical
  sections or queues, not ad-hoc locks in drivers.
- Linux: use the IIO/subsystem or userspace bus; respect scheduling and caching.
- Document the chosen trigger and its jitter evidence per platform.

## 7. Coding Practices
- One context struct per sensor instance; no global device state.
- Typed error enum (ERR_OK, ERR_TIMEOUT, ERR_NACK, ERR_CRC, ERR_RANGE, ...).
- Named constants for all registers, masks and scale factors; no magic numbers.
- Bus access only through an abstract interface (spi_if_t / i2c_if_t).
- RTOS-agnostic drivers: no delays, mutexes or busy-waits inside drivers.
- Deterministic execution time for filters and conversion.

## 8. Error Handling
Handle and classify at minimum:
- NACK / address not acknowledged.
- Timeout on any bus transaction.
- CRC or checksum failure on read.
- Out-of-range or stuck-at values.
- Communication loss and device not present.
Propagate typed errors; never silently substitute a default value. Record
faults for diagnostics (axiom-sensor-diagnostics).

## 9. Security and Safety
- Validate all inputs and ranges; reject out-of-range configuration.
- Do not expose raw bus access to untrusted callers.
- For safety-relevant sensors, treat acquisition as a safety function and apply
  the project safety process; never claim certification from this skill.
- Protect calibration and configuration in NVM against unauthorized writes.

## 10. Verification
- Host-side unit tests with mock register backends, including fault injection.
- HIL tests on target hardware with real sensors.
- Timing captures (oscilloscope/logic analyzer) for bus and sample intervals.
- Evidence bundle with captures, test results and traceability.

## 11. Testing
- Unit tests against scripted register models on host.
- Fault injection: NACK, timeout, CRC fail, out-of-range, stuck-at.
- Timing tests for sampling interval and jitter.
- Regression tests for conversion formulas with known inputs.

## 12. Debugging
- No data: check power, wiring, address, init order, pull-ups.
- Wrong values: check conversion formula, endianness, units, scaling.
- Drift: check clock source, temperature, calibration validity.
- Intermittent failures: check bus loading, noise, grounding, timing margins.
- Use logic analyzer captures as primary evidence.

## 13. Evidence Requirements
- Datasheet and reference manual identifiers with versions.
- Bus timing captures and sample interval measurements.
- Unit and HIL test results.
- Calibration records (when applicable).
- Traceability links to requirements and tests.
