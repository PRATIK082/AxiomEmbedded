---
name: axiom-hw-interface-control
title: Hardware Interface Control and Bench Abstraction
description: >
  Controls bench instruments (power supplies over SCPI/VISA, programmable
  relays, oscilloscopes, logic analyzers) through a logical board_config.yaml
  mapping so test cases and agent workflows never hardcode physical pins,
  serial ports, IP addresses, or instrument strings. Enforces idempotent setup
  and fail-safe teardown on every hardware interaction. Use when any SIL, HIL,
  or system test touches physical bench hardware.
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.validation.hw_interface
  domain: all
  maturity: experimental
  safety_critical: false
  activity: sil-hil
  capability_kind: platform
  primary_domain: all
  risk_class: medium
  inputs: [board configuration, instrument inventory, test objective]
  outputs: [bench session, measurement captures, teardown report]
  required_tools: [run_skill]
  optional_tools: [validate_skill]
  lifecycle: [plan, implement, verify, evidence]
  standards: []
  artifact_types: [bench configuration, evidence package]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  related_skills: []
---
# Hardware Interface Control and Bench Abstraction

## Purpose

Own the physical bench behind every hardware-in-the-loop campaign. All
physical addressing lives in exactly one file, `board_config.yaml`, which maps
logical names (`DUT_UART_MAIN`, `PSU_CHANNEL_1`) to physical interfaces
(serial ports, VISA strings, relay channels, IP addresses). Test cases,
Robot keywords, Pytest fixtures, and agent workflows reference logical names
only. Every session is idempotent on setup and fail-safe on teardown (cut
relay power, reset DUT via debugger/GPIO, flush serial buffers) so a failed
test never leaves the bench locked or unsafe.

## When to Use

- Any test touches power supplies, relays, scopes, analyzers, or fault-injection boards.
- A new bench needs onboarding under the logical-name contract.
- Inputs below are available.

## When Not to Use

- Pure simulation campaigns with no physical instruments (see `axiom-sil-hil-bridge`).
- As a substitute for qualified safety/security certification review.

## Required Inputs

- Board configuration file (`board_config.yaml`, schema below).
- Instrument inventory (make/model/capabilities per logical channel).
- Test objective and channel list.

## Optional Inputs

- Calibration certificates, prior teardown reports, bench photos.

## Prerequisites

- `axiom doctor --skip-tests` green.
- Instruments reachable on the bench network/bus; drivers installed.

## Execution Workflow

1. Normalize the request into channels, measurements, and constraints.
2. Load `board_config.yaml`; resolve logical names to physical interfaces.
3. Pre-check: ping each instrument, verify DUT power rails, record firmware hash.
4. Idempotent setup: drive every channel to its defined safe state first.
5. Execute stimulus/capture per the campaign plan (dry-run first).
6. Fail-safe teardown always runs, even on failure: relays open, DUT reset,
   buffers flushed; record the teardown report.
7. Validate structurally (scripts/ plus checklists/); attach captures with timestamps.
8. Summarize assumptions, risks, next actions.

## board_config.yaml Schema

```yaml
version: 1
dut:
  name: logical-board-name
  reset: {method: jlink|gpio|manual, target: DUT_RESET_LINE}
channels:
  DUT_UART_MAIN: {kind: serial, port: /dev/ttyUSB0, baud: 115200}
  PSU_CHANNEL_1: {kind: scpi, visa: USB0::0x1AB1::0x0E11::DP8A0001::INSTR}
  RELAY_DUT_POWER: {kind: relay, board: RELAY_BOARD_0, channel: 3}
  SCOPE_CH1_VCC: {kind: scope, visa: TCPIP0::192.168.1.50::INSTR, channel: 1}
safe_state:
  RELAY_DUT_POWER: open
  PSU_CHANNEL_1: {volts: 0.0, output: off}
```

Rules: logical names match `[A-Z0-9_]+`; physical values live only here;
this file is the single place a bench move requires an edit.

## Decision Rules

- Prefer explicit configuration over invented defaults; flag every assumption.
- No physical address outside `board_config.yaml`; reviewers reject violations.
- Teardown runs unconditionally; teardown failure blocks the campaign verdict.

## Tool Invocations

- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.

## Workflow

Follow Execution Workflow; record per-step evidence in the run manifest.

## Unified Telemetry

Correlate timestamps across firmware serial logs, scope/analyzer captures, and
runner reports into one structured output directory per test run.

## Deliverables

- Validated `board_config.yaml`, bench session log, measurement captures,
  teardown report.

## Acceptance Criteria

- `validate_skill` passes; checklist gates all green; traceability complete.
- Zero hardcoded physical addresses in consuming tests (grep gate).
- Teardown report present for every session, pass or fail.

## Acceptance

- All checklist gates pass; findings carry severity plus evidence plus action.

## Validation Procedure

1. `python skills/axiom-hw-interface-control/scripts/validate.py`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes

- Hardcoded `/dev/ttyUSB0` or VISA strings in test code -> reject at review.
- Skipped teardown leaving relays energized -> bench lockout; fail the campaign.
- Uncalibrated instruments cited as evidence -> require calibration record.

## Guardrails

- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## Bench Self-Discovery

Before pre-check, the bench identifies itself. `scripts/bench_discover.py`
runs in two modes. `--discover` enumerates candidate serial ports on the
host (device nodes on POSIX, COM ports via the registry on Windows) without
touching hardware. With a `board_config.yaml` path it resolves every logical
channel: file-backed ports by existence, network instruments by TCP connect
with a short timeout, and reports resolved versus unresolved names as JSON.
Unresolved logical names block pre-check with a named finding. DUT
self-identification closes the loop: after reset the DUT must emit an
identity banner (firmware name, version, hash) over its console, matched
against the attested hash from `axiom-firmware-lifecycle`; a banner mismatch
fails pre-check before any stimulus.

## labgrid Mapping

Where Labgrid drives the bench, logical names map one-to-one onto Labgrid
concepts: a channel is a resource, a board plus its channels is a place, a
stimulus or capture action is a driver, shared rigs are served through the
exporter with per-place locking. `board_config.yaml` stays the single source
of truth; Labgrid environment files are generated from it, never hand-kept
in parallel.

## With-Harness and Without-Harness Variants

Every campaign declares its harness mode up front. With-harness runs bind
logical channels to Labgrid places or the physical rig and execute the full
pre-check. Without-harness runs execute host-side and virtual-target cases
only (unit, simulation, virtual-ECU suites tagged `no-harness`); any case
requiring a channel is skipped with a recorded reason, never silently
dropped. Promotion from without-harness to with-harness reuses the same
suites (see `axiom-sil-hil-bridge`).

## Boundary End-Caps

- Lower end-cap: no session starts without a validated `board_config.yaml`
  resolving all channels the campaign needs, or an explicit no-harness
  declaration recorded in the manifest.
- Upper end-cap: every session ends with a teardown report (relays opened,
  DUT reset, buffers flushed) attached to the run, pass or fail.
- Out of scope: instrument calibration (certificates are inputs, not
  outputs), bench electrical safety sign-off, and shared-rig scheduling
  beyond per-place locking.

## Advanced V&V patterns (P1)

### Multi-DUT bench orchestration `[HIGH]`
Synchronize multiple DUTs with per-device options (identity, firmware hash,
channel map); share one suite parameterized per DUT. Required for gateway
and multi-node campaigns.

### RESD sensor replay `[MEDIUM]`
Deterministic replay of recorded sensor streams through bench channels;
preserve timestamps and sampling cadence; document fidelity limits.

### Labgrid managed resources `[MEDIUM]`
Coordinator/exporter/RemotePlace with managed resources bound via udev;
Strategy pattern for boot states (off/bootloader/application); per-place
locking for shared rigs.

## Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| HW-R1 | ISO 26262-4 S7 | HW/SW interface verification |
| HW-R2 | ISTQB CT-TAE | Automation architecture |






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.



## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | (none declared) | LOW |


## Impact tiers

| Tier | Meaning |
|---|---|
| CRITICAL | Safety/security-critical; requires human approval and impact assessment |
| HIGH | Significant impact; requires review |
| MEDIUM | Moderate impact; standard review |
| LOW | Minor impact; routine review |

### Rule impact assignments

All rules in this skill default to MEDIUM unless marked CRITICAL or HIGH
in the rule ID -> clause map above.

## Deviation management

Any deviation must be recorded with: Rule ID, reason, file/location,
approver, and date. CRITICAL-rule deviations require safety-lead approval
and an impact assessment. Deviations are first-class artifacts, not comments.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## References

- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `axiom-validation-orchestrator`, `axiom-sil-hil-bridge`,
  `axiom-bus-protocol-validation`, `axiom-validation-levels`.
