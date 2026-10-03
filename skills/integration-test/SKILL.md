# Integration-Test skill

Verification of unit interactions and HW/SW interfaces: module integration,
driver/hardware integration, and subsystem integration up to HIL — the middle
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
| 1 | ISO 26262-6 Software level | 2018 | §10 software integration and testing, Table 10 methods per ASIL | `https://www.iso.org/standard/68389.html` |
| 2 | ISO 26262-4 System level | 2018 | §7 system integration, hardware-software interface verification | `https://www.iso.org/standard/68386.html` |
| 3 | ISTQB Certified Tester | CTFL v4.0 (2023); CT-ATLaS agile track | Integration test levels and entry/exit criteria | `https://www.istqb.org/certifications/certified-tester-foundation-level/` |

## 3. Integration strategy rules

1. **Incremental, interface-ordered.** Integrate in dependency order with stubs
   for not-yet-ready units; each increment adds one interface and its tests.
   Big-bang integration is a planning defect.
2. **Test the interface, not the units.** Integration cases target data flow,
   sequencing, error propagation, resource contention, and timing across the
   boundary — re-running unit cases at this level wastes the rig.
3. **Hardware-in-the-loop early.** Driver and bus integration runs on target
   from the first increment (dev boards, then EVT hardware); host-only
   simulation of peripheral timing is not integration evidence.
4. **Fault injection at boundaries.** Every interface test plan includes
   corrupted data, timeouts, bus errors, and peer-reset cases — the failure
   modes units never see in isolation (feeds `fault-injection` campaigns).
5. **Rig qualification.** HIL rigs are calibrated and versioned (hardware rev,
   fixture SW, scripts); a test failure must be attributable to product or rig
   unambiguously — otherwise the rig, not the product, is debugged first.

## 4. Timing integration

Measure end-to-end latencies across integrated paths (sensor → processing →
actuator) under load; compare against budgets allocated in `architecture` §3
and WCET analysis in `rtos` §5. Budget overruns at integration trigger
re-allocation with an ADR, not silent margin consumption.

## 5. Exit gates (blocking)

1. All planned interfaces integrated in dependency order with evidence per link.
2. Interface fault-injection cases pass; error propagation matches the
   architecture error model.
3. Timing measurements within allocated budgets on target hardware.
4. Rig configuration recorded; failures attributable product-vs-rig.
5. Traceability updated: every software integration requirement has its test
   result in the matrix.

## 6. Verification of this skill (Phase 4 gate)

- No big-bang integration accepted as a strategy.
- Timing evidence measured on target, not simulated.
