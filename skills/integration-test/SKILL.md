---
name: integration-test
description: >
  Incremental integration strategy, HIL discipline, and timing integration. Use
  when bringing up combined HW/SW or planning integration stages.
version: 1.3.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.integration-test
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy, vv, integration]

  related_skills: [axiom-hil-test-planning, axiom-test-automation, axiom-validation-orchestrator]
  checklists: [checklists/integration-test-checklist.md]

  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: []
  optional_tools: []
---

# Integration-Test skill

Verification of unit interactions and HW/SW interfaces: module integration,
driver/hardware integration, and subsystem integration up to HIL -- the middle
levels of the V-model right arm.

## 1. Purpose and scope

**Purpose.** Prove that units which pass in isolation work together and against
real hardware peripherals, buses, and timing.

**In scope.** Integration strategy (big-bang never; incremental top-down /
bottom-up / sandwich), interface test harnesses, driver-on-target testing,
bus/protocol conformance (I2C/SPI/UART/CAN/Ethernet), timing integration, and
HIL rig design and qualification.

**Non-goals.** Single-unit verification (see `unit-test`), end-to-end system
behavior (see `system-test`).

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-6 Software level | 2018 | S10 software integration and testing, Table 10 methods per ASIL | `https://www.iso.org/standard/68389.html` |
| 2 | ISO 26262-4 System level | 2018 | S7 system integration, hardware-software interface verification | `https://www.iso.org/standard/68386.html` |
| 3 | ISTQB Certified Tester | CTFL v4.0 (2023); CT-ATLaS agile track | Integration test levels and entry/exit criteria | `https://www.istqb.org/certifications/certified-tester-foundation-level/` |

## 3. Integration strategy rules

1. **Incremental, interface-ordered.** `[CRITICAL]` Integrate in dependency
   order with stubs for not-yet-ready units; each increment adds one interface
   and its tests. Big-bang integration is a planning defect.
2. **Test the interface, not the units.** `[HIGH]` Integration cases target
   data flow, sequencing, error propagation, resource contention, and timing
   across the boundary -- re-running unit cases at this level wastes the rig.
3. **Hardware-in-the-loop early.** `[HIGH]` Driver and bus integration runs on
   target from the first increment (dev boards, then EVT hardware); host-only
   simulation of peripheral timing is not integration evidence.
4. **Fault injection at boundaries.** `[CRITICAL]` Every interface test plan
   includes corrupted data, timeouts, bus errors, and peer-reset cases -- the
   failure modes units never see in isolation (feeds `fault-injection`
   campaigns).
5. **Rig qualification.** `[HIGH]` HIL rigs are calibrated and versioned
   (hardware rev, fixture SW, scripts); a test failure must be attributable to
   product or rig unambiguously -- otherwise the rig, not the product, is
   debugged first.

## 4. Timing integration

Measure end-to-end latencies across integrated paths (sensor -> processing ->
actuator) under load; compare against budgets allocated in `architecture` S3
and WCET analysis in `rtos` S5. Budget overruns at integration trigger
re-allocation with an ADR, not silent margin consumption.

## 5. Advanced V&V patterns (P1)

### 5.1 Multi-DUT testing `[HIGH]`
Synchronize multiple DUTs with per-device options (identity, firmware hash,
channel map). Share one suite; parameterize per DUT. Required for gateway,
multi-node bus, and redundancy tests.

### 5.2 Labgrid architecture `[MEDIUM]`
Adopt coordinator/exporter/RemotePlace model: managed resources bound to
places, Strategy pattern for boot states (off/bootloader/application). Shared
rigs served via exporter with per-place locking. Generate Labgrid env files
from `board_config.yaml`.

### 5.3 RESD sensor replay `[MEDIUM]`
Deterministic HIL sensor-data replay using recorded sensor streams (RESD) so
integration cases reproduce field conditions. Replay must preserve timestamps
and sampling cadence; document replay fidelity limits.

### 5.4 Cloud emulation for hardware-free CI `[MEDIUM]`
Use Wokwi/esp-emu/QEMU for hardware-free integration smoke in CI; promote to
physical rig before release. Emulation covers logic only; timing claims need
hardware.

## 6. Exit gates (blocking)

1. All planned interfaces integrated in dependency order with evidence per link.
2. Interface fault-injection cases pass; error propagation matches the
   architecture error model.
3. Timing measurements within allocated budgets on target hardware.
4. Rig configuration recorded; failures attributable product-vs-rig.
5. Traceability updated: every software integration requirement has its test
   result in the matrix.

## 7. Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| IT-R1 | ISO 26262-6 S10, Table 10 | Software integration test methods per ASIL |
| IT-R2 | ISO 26262-4 S7 | System integration and HW/SW interface verification |
| IT-R3 | ISO/IEC/IEEE 29119-2 | Test process and entry/exit criteria |

## 8. Verification of this skill (Phase 4 gate)

- No big-bang integration accepted as a strategy.
- Timing evidence measured on target, not simulated.

## Workflow

Follow the skill's numbered rules and gates; record per-step evidence in the
run manifest.

## Acceptance

All checklist gates pass; findings carry severity plus evidence plus action.

## References

- `references/standard-map.md`
- `references/vv-patterns.md`
