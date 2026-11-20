---
name: axiom-sil-hil-bridge
title: SIL-to-HIL Promotion Bridge
description: >
  Runs identical test logic against a virtual target (QEMU/Renode) first, then
  promotes the exact same validation criteria to physical HIL hardware with
  timing tolerances widened for real-world latency. Tracks per-case SIL status,
  HIL status, and tolerance deltas so no SIL pass is ever reported as hardware
  proof. Use when a campaign must graduate simulation cases to the bench
  without rewriting assertions.
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.validation.sil_hil_bridge
  domain: all
  maturity: experimental
  safety_critical: false
  activity: sil-hil
  capability_kind: validator
  primary_domain: all
  risk_class: medium
  inputs: [SIL test cases, plant model, tolerance policy, bench configuration]
  outputs: [HIL test suite, tolerance map, promotion report, run manifest]
  required_tools: [run_skill]
  optional_tools: [validate_skill]
  lifecycle: [plan, implement, verify, evidence]
  standards: []
  artifact_types: [HIL test suite, promotion report, evidence package]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  related_skills: []
---
# SIL-to-HIL Promotion Bridge

## Purpose

Graduate simulation cases to hardware without rewriting assertions. The same
test logic runs first against a virtual target (QEMU/Renode with a plant
model), then against physical HIL hardware with timing tolerances widened per
an explicit tolerance policy. Every case carries both verdicts plus the
tolerance delta, so a SIL pass can never be mistaken for hardware proof.

## When to Use

- A SIL suite exists and must be promoted to the HIL bench.
- Timing-sensitive assertions need explicit SIL-vs-HIL tolerance mapping.
- Inputs below are available.

## When Not to Use

- As a substitute for qualified safety/security certification review.
- When no plant model or virtual target exists (build SIL first; never skip to HIL-only).

## Required Inputs

- SIL test cases with assertions and current tolerances.
- Plant model plus simulator version (QEMU/Renode, model revision).
- Tolerance policy (which assertions widen on HIL, by how much, and why).
- Bench configuration (`board_config.yaml` logical names).

## Optional Inputs

- Prior promotion reports, historical tolerance deltas, bench calibration data.

## Prerequisites

- `axiom doctor --skip-tests` green.
- SIL suite green on the virtual target; firmware identity attested
  (`axiom-firmware-lifecycle`).
- Bench provisioned via `axiom-hw-interface-control`.

## Execution Workflow

1. Normalize the request into SIL cases, assertions, and tolerances.
2. Freeze the SIL baseline: record simulator, model revision, and verdicts.
3. Apply the tolerance policy: map each timing assertion to its HIL tolerance
   with rationale; functional assertions stay identical.
4. Generate the HIL suite (dry-run first): same logic, widened tolerances,
   logical bench names only.
5. Pre-check the bench, flash the attested image, execute on hardware.
6. Record per-case SIL status, HIL status, and tolerance delta in the
   promotion report.
7. Validate structurally (scripts/ plus checklists/).
8. Summarize assumptions, risks, next actions.

## Decision Rules

- Functional assertions are identical across SIL and HIL; only timing
  tolerances change, and each change carries a rationale.
- A case that passes SIL but fails HIL is a HIL finding, never a SIL waiver.
- SIL results are never reported as hardware evidence; the promotion report
  keeps both verdicts visible.
- Prefer explicit configuration over invented defaults; flag every assumption.

## Tool Invocations

- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.

## Workflow

Follow Execution Workflow; record per-step evidence in the run manifest.

## Tolerance Policy Shape

```yaml
version: 1
rules:
  - assertion: can_frame_period_ms
    sil_tolerance: {plus_minus_ms: 0.5}
    hil_tolerance: {plus_minus_ms: 2.0}
    rationale: bus arbitration plus transceiver delay on hardware
  - assertion: boot_complete
    sil_tolerance: {timeout_s: 5}
    hil_tolerance: {timeout_s: 15}
    rationale: flash read-back plus regulator ramp on hardware
```

Every widened tolerance cites a physical cause; blanket multipliers are rejected.

## Deliverables

- HIL test suite, tolerance map with rationales, promotion report with
  per-case dual verdicts.

## Acceptance Criteria

- `validate_skill` passes; checklist gates all green; traceability complete.
- Every timing tolerance change carries a physical-cause rationale.
- Promotion report shows SIL and HIL verdicts side by side for every case.

## Acceptance

- All checklist gates pass; findings carry severity plus evidence plus action.

## Validation Procedure

1. `python skills/axiom-sil-hil-bridge/scripts/validate.py`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes

- Reporting SIL pass as hardware proof -> explicitly forbidden.
- Blanket 2x tolerance multiplier without per-assertion rationale -> reject.
- HIL failure waived because SIL passed -> reject; file a HIL finding.

## Guardrails

- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## Virtual-ECU Adapter Pattern

Identical test logic binds to two adapters behind one keyword layer: a
virtual adapter speaking to a simulated ECU service (REST or model API fed
by the QEMU/Renode plant) for SIL, and a physical adapter driving bench
channels for HIL. Suites import the adapter by variable file, so SIL runs
select the virtual binding and HIL runs select the physical binding with no
suite edits. Adapter responses carry source labels, keeping virtual
evidence visibly distinct from hardware evidence in every report.

## Fault Parity

The fault set is defined once and executed in both worlds: brownouts, bus
faults, sensor freezes, and packet drops run against the plant model in SIL
and against the rig in HIL. Recovery behavior is compared case by case;
divergence is analyzed as model fidelity data (missing peripheral model,
unmodeled latency, idealized fault shape) and recorded in the fidelity log,
never dismissed. Update-path faults from `axiom-firmware-lifecycle` join
the parity set where the virtual target models storage.

## Model Fidelity Log

Every promoted campaign maintains a fidelity log: simulator plus version,
plant model revision, modeled versus unmodeled peripherals, known timing
idealizations, and prior SIL/HIL divergences with disposition. New
divergences update the log; repeated unexplained divergence blocks further
promotion until the model or the tolerance policy is corrected.

## Boundary End-Caps

- Lower end-cap: no promotion without a frozen green SIL baseline (simulator,
  model revision, and verdicts recorded) plus an explicit tolerance policy.
- Upper end-cap: promotion report shows SIL verdict, HIL verdict, tolerance
  delta, and fidelity notes side by side for every case.
- Out of scope: plant-model development or calibration (models are inputs
  with versions; tuning them is a separate workstream recorded as such).

## Advanced V&V patterns (P1)

### Co-simulation `[MEDIUM]`
Verilator/SystemC/FPGA co-simulation for early SIL; promote sampled cases to
HIL. Record simulator and model versions in the fidelity log.

### RESD sensor replay `[MEDIUM]`
Deterministic replay of recorded sensor streams in both SIL and HIL; preserve
timestamps and sampling cadence.

### Cloud emulation `[MEDIUM]`
Wokwi/esp-emu/QEMU for hardware-free SIL smoke; promotion to physical rig
remains mandatory for release claims.

### Panic/core-dump decoding `[HIGH]`
Automated backtrace decode on failure in either world; attach decoded trace
to the promotion report.

### Multi-DUT promotion `[HIGH]`
Promote multi-DUT scenarios with per-device tolerance maps; keep dual
verdicts per DUT.

## Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| SH-R1 | ISO 26262-6 S9/S10 | Unit and integration verification |
| SH-R2 | ISO/IEC/IEEE 29119 | Test process and reporting |


## Deviation management

Any deviation from a rule or standard must be recorded with: Rule ID, reason,
file/location, approver, and date. Deviations are tracked as first-class
artifacts, not comments. (Straion pattern.)


## Builder + reviewer

This skill follows the builder + reviewer pattern: the builder produces the
artifact, the reviewer independently verifies it before acceptance. No
artifact is accepted without reviewer sign-off.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## References

- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `axiom-validation-orchestrator`, `axiom-hw-interface-control`,
  `axiom-bus-protocol-validation`, `axiom-firmware-lifecycle`,
  `axiom-validation-levels`, `axiom-mil-sil-hil-testing`.
