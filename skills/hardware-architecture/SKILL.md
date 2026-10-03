# Hardware-Architecture skill

Board and SoC-level hardware architecture for embedded products: requirement
allocation to electronics, block design, power/signal-integrity budgets,
component selection, and the hardware evidence (schematics, layout, bring-up
data) software depends on.

## 1. Purpose and scope

**Purpose.** Define electronics that meet functional, power, thermal, EMC, and
cost requirements with margins — and hand software a truthful hardware model
(datasheets, errata, memory maps, timing) instead of surprises.

**In scope.** Requirements allocation to hardware, block diagrams and interface
budgets, component selection (MCU/MPU, memories, power, clocks, sensors),
power-distribution and signal-integrity analysis, schematic/layout review
checkpoints, hardware-software interface specification (memory map, registers,
interrupts, boot config), and revision control of hardware baselines.

**Non-goals.** Detailed PCB layout execution and manufacturing engineering.
Ends at reviewed fabrication outputs plus the HSI document software builds
against.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | IPC-2221 PCB design | Generic standard, current revision B | Land patterns, conductor sizing, design rules baseline | `https://www.ipc.org/ipc-2221-generic-printed-board-design` |
| 2 | ISO 26262-5 Hardware level | 2018 | Hardware architectural design, metrics (SPFM/LFM), dependent-failure analysis | `https://www.iso.org/standard/68387.html` |
| 3 | DO-254 Airborne hardware | 2000 | Design assurance levels, lifecycle data for custom electronics | `https://www.rtca.org/products/design-assurance-guidance-for-airborne-electronic-hardware-do-254/` |
| 4 | EMC-CE/FCC regimes | IEC 61000 series; FCC Part 15 (US) | Emissions/immunity targets the layout must meet | `https://www.fcc.gov/oet/ea/rfdevice` |

## 3. Design rules

1. **Budget before schematic.** Power (rail × current with margin), thermal
   (θJA paths, worst-case ambient), signal integrity (length/skew/impedance
   for DDR, USB, Ethernet), and BOM cost close before layout starts.
2. **Datasheet-plus-errata is the contract.** Every active component ships
   with its errata reviewed and silicon bugs allocated (hardware workaround,
   driver workaround per `drivers` §2, or accepted risk) — see
   `hardware-bringup` for validation.
3. **HSI document.** Memory map, register definitions, interrupt assignments,
   clock tree, reset sequencing, boot-mode strapping, and power-domain
   behavior written once, reviewed by software, versioned with the board
   revision. Undocumented hardware behavior is a blocking defect.
4. **Design for test and bring-up.** Test points on critical nets, JTAG/SWD
   access, UART console, current-measurement jumpers, and unpopulated debug
   headers cost pennies and save weeks.

## 4. Review checkpoints (blocking)

Concept/block review → schematic review (with software present for the HSI) →
layout review (placement, stackup, return paths, EMC) → fabrication-release
audit (BOM, alternates, lifecycle status) → bring-up report per
`hardware-bringup`. No checkpoint is skipped; waivers carry expiry and owner.

## 5. Release gates (blocking)

1. Budgets close with margin; component lifecycle covers the product horizon.
2. HSI reviewed and versioned; errata dispositions complete.
3. Bring-up report confirms the hardware matches its model (or records
   deviations with software impact assessed).

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL (§2).
