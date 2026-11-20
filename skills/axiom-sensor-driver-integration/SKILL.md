---
name: axiom-sensor-driver-integration
title: Sensor Driver Integration
description: >
  Integrates a sensor chip over I2C, SPI, UART or 1-Wire into a layered device
  driver with register encapsulation, context structs, identification, typed
  errors and mockable bus seams. Use when sensor driver integration tasks arise
  in generic-embedded projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [generic-embedded, iot, industrial, automotive, robotics]
platforms: [mcu, mpu, soc, mpsoc]

axiom:
  dotted_name: axiom.generic-embedded.sensor.driver.integration
  domain: generic-embedded
  subdomain: sensor
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [sensor, driver, i2c, spi, uart, register-map]

  related_skills: [axiom-sensor-acquisition, axiom-sampling-timestamping, drivers, unit-test]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [device driver, register map header, integration evidence]
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
# Axiom Sensor Driver Integration

## Purpose
Integrates a specific sensor chip into a layered, reusable device driver. Covers
register-map encapsulation, device context, init and identification sequences,
configuration, burst reads, error propagation and mockable bus seams.

Scope: sensor driver integration (generic-embedded). Maturity: experimental. This
skill is original AxiomEmbedded content.

## When to Use
- Adding a new sensor chip (BMP280, MPU6050, ICM42688, etc.) to a platform.
- Porting a sensor driver across MCU families.
- Refactoring a driver that leaks HAL or global state.

## When Not to Use
- For bus-level driver work (use drivers).
- For acquisition architecture decisions (use axiom-sensor-acquisition).
- For calibration (use axiom-sensor-calibration).

## Required Inputs
- Repository path and target file list.
- Sensor datasheet and register map.
- Bus type and speed; MCU family and HAL.
- Required features (sampling rate, ranges, interrupts).

## Optional Inputs
- Existing driver code, errata, logic analyzer captures.
- Mock register model for host tests.

## Prerequisites
- Bus driver exposing spi_if_t / i2c_if_t / uart_if_t.
- Unified error_t enum available.
- Host test harness with mock bus.

## Execution Workflow
1. Normalize the request into objective, scope and constraints.
2. Inspect repo context and existing driver artifacts.
3. Define the register map header (_reg.h).
4. Define the device context struct.
5. Implement init, identify, configure, read, error propagation.
6. Add mockable bus seam and host tests.
7. Validate structurally and semantically.
8. Run checks and record results.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks and next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Device drivers depend on bus interfaces, never on vendor HAL types.
- No global device state; state lives in a context struct.
- Register addresses and bit-fields only in _reg.h.
- RTOS-agnostic: no delays, mutexes or busy-waits in drivers.
- Typed errors only; no magic -1 / -2.

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-sensor-driver-integration/`.
- Device driver source, header and _reg.h.
- Mock bus tests and evidence.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.
- Driver contains no HAL API calls or MCU-specific types.
- Host unit tests with mock bus green.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-sensor-driver-integration`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Register leakage into driver code -> move constants to _reg.h.
- Global state prevents multi-instance use -> encapsulate in context struct.
- HAL types in device driver -> depend on bus interface only.
- Busy-waits and RTOS calls in driver -> remove; use timeouts/callbacks.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not silently alter user code outside the declared change scope.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| drivers-register-access-discipline | Register access discipline | MEDIUM |
| safety-io-matrix | Safety I/O matrix | MEDIUM |
| misra-c-driver-hygiene | Driver hygiene | LOW |

## Impact tiers

| Impact tier | Meaning | Typical handling |
|---|---|---|
| CRITICAL | Safety/security-critical; release blocker; core/evidence zone | Human approval required; no autonomous AI action |
| HIGH | Major correctness or compliance impact | Reviewed change; evidence required |
| MEDIUM | Moderate impact | Standard review |
| LOW | Minor or advisory | Batched review acceptable |

### Rule impact assignments

| Rule ID | Impact tier |
|---|---|
| drivers-register-access-discipline | MEDIUM |
| safety-io-matrix | MEDIUM |
| misra-c-driver-hygiene | LOW |

## Deviation management

Any deviation from a rule or standard in this skill must be recorded as a
first-class artifact (not a code comment) with all of the following:

- Rule ID
- Reason
- File / location
- Approver
- Date

Deviations against CRITICAL rules require a safety/security lead approval and
an impact assessment. Store deviation records under the project evidence or
change-control location and link them in the traceability matrix.

## Builder + reviewer pairing

This skill produces reviewable artifacts. Its outputs must be
independently checked by a human reviewer or the domain review skill
before acceptance; solo use requires an explicit waiver recorded in
the deviation log.

## Three-zone autonomy

Autonomy is zoned by risk; the V&V boundary is the automation boundary.

- Core / evidence zone (AI no access, human accountable): certified or
  qualified artifacts, evidence records, safety/security-critical code, and
  release baselines. AI must not read or write here without an explicit
  human-approved change request.
- Gray zone (AI assistant + HITL): AI plans and drafts; a human decides and
  approves each step. Architecture, requirements, tests with safety impact,
  and verification-affecting configuration live here.
- Non-critical zone (AI unrestricted): documentation, examples, scaffolding,
  low-risk refactors, and tooling glue.

This skill's outputs are treated as gray-zone by default; AI may draft but
a human approves. AI must never act autonomously in the core/evidence zone.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no
  normative text.

## 1. Layered Driver Architecture
Stack:
APP -> MODULE -> INTERFACE -> DEVICE DRIVER -> BUS DRIVER -> HAL/BSP -> vendor HAL.
Device drivers never call HAL directly and never contain application policy
(PID, Kalman, state machines). Bus drivers own MCU-specific bus peripherals.

## 2. Directory Structure
driver/
  bus/     spi/ i2c/ uart/ can/
  device/  bmp280/ (bmp280.c, bmp280.h, bmp280_reg.h)
           mpu6050/
  common/  error.h types.h
BSP resources (LED, button, buzzer) belong under bsp/, not driver/.

## 3. Bus Abstraction
Every bus exposes an abstract interface; device drivers depend only on it.
- SPI: spi_if_t with transfer, transfer_async.
- I2C: i2c_if_t with write, read, write_read.
- UART: uart_if_t with write, read, read_until.
Forbidden in device drivers: SPI_HandleTypeDef, HAL_SPI_Transmit. Required:
bus->transfer(tx, rx, len). The interface must be mockable via function pointers.

## 4. Register Encapsulation
All register addresses and bit-fields live in _reg.h. Example pattern:
- BMP280_REG_CHIP_ID 0xD0
- BMP280_REG_CTRL_MEAS 0xF4
- BMP280_CHIP_ID_VALUE 0x58
No magic addresses scattered in driver code. Bit definitions are named constants
with width and mask documented from the datasheet.

## 5. Device Context
struct bmp280_dev {
    i2c_if_t *bus;
    uint8_t addr;
    uint8_t chip_id;
    /* calibration coefficients */
    /* current config */
};
All state lives here. Enables multiple instances on different bus channels.

## 6. Init and Identification
error_t xxx_init(xxx_t *dev);
Steps: validate params, check bus present, read WHO_AM_I / chip ID, compare to
expected value, apply init sequence from datasheet, load calibration, set
configured flag. Return typed error on any mismatch. Never assume identification
succeeds.

## 7. Configuration
Expose typed setters for sampling rate, range, filters. Each writes the
corresponding register(s) and verifies by read-back when the datasheet requires.
Reject out-of-range values with ERR_INVALID_PARAM.

## 8. Read Burst
Read all needed registers in one burst transaction when possible to keep a
consistent sample. Parse fields with named shifts/masks. Validate CRC or
checksum when the sensor provides one; return ERR_CRC on mismatch.

## 9. Error Propagation
All functions return error_t. Map bus errors to ERR_COMMUNICATION, timeouts to
ERR_TIMEOUT. Never swallow errors. Log or record faults for diagnostics. Avoid
partial updates on failure (restore or mark not-ready).

## 10. RTOS and Timing Isolation
Drivers are RTOS-agnostic: no osDelay, vTaskDelay, osMutexAcquire, no
busy-wait loops. Use timeout/callback/event mechanisms. DMA streams and IRQ
numbers stay in the bus layer; the device driver chooses sync vs async but
does not configure DMA hardware.

## 11. Mock Testing
Every bus interface must be mockable. Tests script register responses and
inject faults (NACK, timeout, short read, CRC fail). Verify init rejection on
wrong chip ID, correct parsing of burst reads and error propagation.

## 12. Evidence
- Logic analyzer captures of init and read transactions.
- Unit test results with mock bus.
- Errata workaround references and tests.
- Review of register map against datasheet.
