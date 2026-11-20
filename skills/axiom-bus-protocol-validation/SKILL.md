---
name: axiom-bus-protocol-validation
title: Bus and Protocol Validation Routines
description: >
  Validates embedded communication buses and protocol stacks -- UART, CAN/CAN-FD,
  SPI, I2C, Ethernet/MQTT, and BLE -- with reusable frame builders, packet
  parsers, and bidirectional checks: software-to-hardware (register writes and
  RTOS events produce expected voltages, PWM, frames, logs) and
  hardware-to-software (injected bus faults trigger expected interrupts, error
  flags, and recovery). Use when any test campaign must prove protocol behavior
  on the wire, not just in the source.
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.validation.bus_protocol
  domain: all
  maturity: experimental
  safety_critical: false
  activity: verification
  capability_kind: validator
  primary_domain: all
  risk_class: medium
  inputs: [protocol specification, frame definitions, test objective]
  outputs: [parser library, validation report, run manifest]
  required_tools: [run_skill]
  optional_tools: [validate_skill]
  lifecycle: [plan, implement, verify, evidence]
  standards: []
  artifact_types: [validation report, evidence package]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  related_skills: []
---
# Bus and Protocol Validation Routines

## Purpose

Prove protocol behavior on the wire. Provides reusable frame builders and
packet parsers for UART, CAN/CAN-FD, SPI, I2C, Ethernet/MQTT, and BLE, plus
bidirectional traceability checks in both directions: software-to-hardware
(firmware actions produce measurable physical outputs) and
hardware-to-software (physical fault injection produces expected firmware
reactions).

## When to Use

- A campaign must validate frames, packets, timing, or error handling on a bus.
- Bus fault injection (brown-out, noise, shorts, packet drops) needs expected-response checks.
- Inputs below are available.

## When Not to Use

- As a substitute for qualified safety/security certification review.
- When the protocol specification is absent (record the gap; never guess frame layouts).

## Required Inputs

- Protocol specification and frame/packet definitions (DBC, ARXML, datasheet section).
- Logical channel names from `board_config.yaml`.
- Test objective and pass thresholds (timing tolerances, error budgets).

## Optional Inputs

- Reference captures, prior validation reports, plant-model timing bounds.

## Prerequisites

- `axiom doctor --skip-tests` green.
- Bench channels provisioned via `axiom-hw-interface-control`.

## Execution Workflow

1. Normalize the request into protocol, frames, directions, and thresholds.
2. Build or reuse the frame builder plus packet parser for the protocol.
3. Software-to-hardware checks: drive firmware actions (register writes, state
   transitions, RTOS events) and assert measurable outputs (voltages, PWM duty,
   CAN/SPI frames, UART logs) within tolerance.
4. Hardware-to-software checks: inject physical faults (brown-outs, sensor
   noise, bus shorts, packet drops) and assert firmware reactions (interrupts,
   error flags, recovery states, DTCs where applicable).
5. Correlate captures with firmware logs by timestamp into the run directory.
6. Validate structurally (scripts/ plus checklists/).
7. Summarize assumptions, risks, next actions.

## Decision Rules

- Frame layouts come from the specification; never invent arbitration IDs,
  signal positions, or CRC polynomials.
- Timing assertions carry explicit tolerances; SIL tolerances widen on HIL
  (see `axiom-sil-hil-bridge`).
- Every fault injected has an expected response declared before injection.
- Prefer explicit configuration over invented defaults; flag every assumption.

## Tool Invocations

- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.

## Workflow

Follow Execution Workflow; record per-step evidence in the run manifest.

## Supported Protocols

| Protocol | Builder | Parser | Fault hooks |
|---|---|---|---|
| UART | frame tx with baud/parity | log line parser | noise, drops, break |
| CAN / CAN-FD | DBC-driven frame builder | signal decoder | bus-off, stuff errors, load |
| SPI | transfer descriptor | MISO capture compare | clock skew, CS glitch |
| I2C | transaction builder | ACK/NACK trace | stretch, NACK, arbitration loss |
| Ethernet / MQTT | topic/payload factory | broker capture diff | drops, duplicates, latency |
| BLE | GATT op builder | notification log | disconnect, MTU, interval jitter |

## Deliverables

- Parser/builder library additions, validation report with per-frame evidence,
  timestamp-correlated captures.

## Acceptance Criteria

- `validate_skill` passes; checklist gates all green; traceability complete.
- Both directions covered (SW-to-HW and HW-to-SW) or the gap is recorded.
- No invented frame layouts; every layout cites its specification source.

## Acceptance

- All checklist gates pass; findings carry severity plus evidence plus action.

## Validation Procedure

1. `python skills/axiom-bus-protocol-validation/scripts/validate.py`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes

- Asserting on simulated timing with HIL-tight tolerances -> widen explicitly.
- Fault injected without declared expected response -> reject at review.
- Parser checked against itself instead of the specification -> require spec citation.

## Guardrails

- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## Positive, Negative, and Failure Triplets

Every protocol campaign ships triplets, not single happy-path checks:

| Protocol | Positive | Negative (boundary rejection) | Failure (fault plus fail-safe) |
|---|---|---|---|
| UART | framed exchange at baud plus parity | framing error on wrong parity | break condition plus noise burst recovers to resync |
| CAN / CAN-FD | DBC-signal round trip within period | DLC mismatch rejected | bus-off injection reaches bus-off then recovers per policy |
| SPI | MISO capture equals expected | CS glitch aborts transfer cleanly | clock skew beyond tolerance flags error, no silent shift |
| I2C | ACKed transaction trace | NACK on missing address | arbitration loss retries then reports, no bus hang |
| Ethernet / MQTT | broker diff equals expected | oversize payload rejected | drop plus duplicate storm stays within latency budget |
| BLE | GATT notify sequence complete | MTU downgrade handled | disconnect mid-transfer reconnects and resumes or fails safe |

## Security and Fuzz Checks

Protocol validation includes adversarial cases, scaled to bench safety:

- Fuzz each parser with malformed, truncated, and oversized frames; the DUT
  must reject or contain, never crash, hang, or execute.
- CAN: fuzz arbitration IDs and payloads; verify error-frame accounting and
  no transmit lockup under load.
- UART plus debug consoles: injection of escape sequences and oversized
  lines; verify no shell escape or buffer overrun.
- MQTT: authentication failure, ACL violation, and oversized topic or payload
  rejected; broker credentials never stored in test files.
- BLE: pairing downgrade attempts and malformed GATT operations rejected;
  link-loss behavior verified.
- Correlate third-party stacks (RTOS network components, MQTT clients)
  against known CVEs and record the triage with the report.
- Fuzz runs carry the `security` tag and run with-harness only where a
  fault could disturb shared equipment; otherwise they run against the
  virtual ECU first.

## Boundary End-Caps

- Lower end-cap: no bus case runs without a cited specification source for
  its frame layout (DBC, ARXML, datasheet section) plus provisioned logical
  channels.
- Upper end-cap: report covers both directions (SW-to-HW, HW-to-SW) with
  per-frame evidence, or records the uncovered direction as a gap.
- Out of scope: RF-layer conformance, protocol stack certification testing,
  and penetration testing beyond interface fuzzing (hand off with captures).

## Advanced V&V patterns (P1)

### Property-based testing `[HIGH]`
Property tests for frame parsers and codecs (round-trip, idempotence,
monotonicity); shrink failures to minimal counterexamples.

### Fuzzing lifecycle `[HIGH]`
Coverage-guided fuzzer harness per parser; maintain seed corpus; triage
crashes into minimal reproducers and regression tests.

### Multi-node bus testing `[HIGH]`
Synchronized multi-DUT bus scenarios with per-node options; required for
gateway and redundancy cases.

### RESD sensor replay `[MEDIUM]`
Deterministic replay of recorded bus/sensor traffic for reproducible fault
and abuse cases.

## Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| BP-R1 | ISO 26262-6 S10 | Software integration and interface testing |
| BP-R2 | ISO 11898 (CAN) | CAN protocol conformance (identifier only) |

## References

- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `axiom-hw-interface-control`, `axiom-sil-hil-bridge`,
  `axiom-validation-orchestrator`, `axiom-validation-levels`.
