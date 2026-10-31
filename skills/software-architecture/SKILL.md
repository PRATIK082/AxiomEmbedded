---
name: software-architecture
description: Embedded software layering, concurrency design, and variability without forks. Use when structuring firmware/software tasks, partitions, or product lines.
version: 1.3.0
domains: [all]
platforms: [all]
axiom:
  dotted_name: axiom.legacy.software-architecture
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills:
  - axiom-platform-architecture-review
  checklists:
  - checklists/software-architecture-checklist.md
---

# Software-Architecture skill

Software architecture for firmware and embedded applications: layered design,
concurrency architecture, resource budgets, variability management, and the
evaluation evidence that the structure satisfies timing, safety, and
maintainability requirements.

## 1. Purpose and scope

**Purpose.** Structure software so timing is analyzable, faults are contained,
features are variable without forks, and new engineers can reason about the
system from its views — complementing the system-level `architecture` skill at
software depth.

**In scope.** Layering (HAL, OSAL, services, application), concurrency design
(task decomposition, priorities, IPC selection per `rtos`), state-machine
discipline, configuration and variability (build-time vs run-time),
error-handling architecture, update partitioning (A/B per `bootloader`), and
software architecture evaluation.

**Non-goals.** System allocation and hardware design (see `architecture`,
`hardware-architecture`). Starts at allocated software requirements, ends at
an evaluated software architecture with ADRs.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 42010 | 2022 | Views, viewpoints, correspondence, rationale | `https://www.iso.org/standard/50508.html` |
| 2 | ISO 26262-6 Software level | 2018 | Clause 7 software architectural design, freedom from interference | `https://www.iso.org/standard/68389.html` |
| 3 | AUTOSAR Classic BSW/RTE layering | R24-11 baseline (Doc ID 53) | Layer boundaries, RTE contracts | `https://www.autosar.org/standards/classic-platform/` |

## 3. Design rules

1. **Strict layering with dependency direction.** Application → services →
   OSAL → HAL → drivers; upward dependencies forbidden, layer-skipping
   forbidden. The dependency rule is enforced by build structure (separate
   libraries, private include paths), not by convention.
2. **Concurrency architecture first.** Task table (period, priority, WCET
   budget, core assignment) precedes task code; shared resources use ceiling
   protocols; ISR/task contracts follow `rtos` §4–§5.
3. **State machines explicit.** Control behavior modeled as hierarchical state
   machines with defined transitions, guards, and timeout handling —
   implemented via tables or qualified generators, never nested-switch
   folklore. Every state has an exit to a safe state.
4. **Variability without forks.** Product variants via configuration (Kconfig,
   devicetree, feature flags with documented lifecycle), never `#ifdef`
   forests or cloned codebases. Each variant builds and tests in CI.
5. **Errors architected.** Error taxonomy, propagation policy (who retries,
   who escalates, who logs), and persistence rules defined once per
   `implementation` §3.3 — not invented per module.

## 4. Baselining gates (blocking)

1. Layer diagram with enforced dependency direction; task table with budgets.
2. State machines documented with safe-state exits.
3. Variant matrix with CI coverage of every shippable variant.
4. ADRs for layering, concurrency, and variability decisions.

## 5. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL (§2).
- Architecture-to-requirement trace maintained in the traceability matrix.



## 7. Firmware project structure and dependency rules

### 7.1 Mandatory project layout
Firmware projects must use:
```
project/
â”œâ”€â”€ app/
â”œâ”€â”€ module/
â”œâ”€â”€ interface/
â”œâ”€â”€ bsp/
â”œâ”€â”€ platform/
â”œâ”€â”€ middleware/
â”œâ”€â”€ docs/
â”œâ”€â”€ tools/
â””â”€â”€ tests/
```
- `app/` â€” state machines, orchestration, startup, task creation. Must not contain register access, HAL calls, or peripheral drivers.
- `module/` â€” business logic (motor, imu, control, telemetry, navigation, power). May depend only on `interface/`. Must not access HAL, CMSIS, GPIO/UART/SPI registers.
- `interface/` â€” hardware abstraction contracts (gpio_if.h, uart_if.h, ...). Contracts only; no implementation.
- `bsp/` â€” board-specific implementation (led, button, buzzer, oled, imu_board). Maps interfaces to hardware; may use platform.
- `platform/` â€” vendor-specific code (platform/<target>/core, hal, cmsis, startup, linker). Contains CubeMX/HAL/CMSIS/startup/linker. Must never contain business logic.
- `middleware/` â€” third-party (freertos, lwip, fatfs, usb). Isolated from application logic.

### 7.2 Dependency rules
Allowed direction (top-down only): `APP â†’ MODULE â†’ INTERFACE â†’ BSP â†’ PLATFORM`. Forbidden: `APP â†’ HAL`, `APP â†’ STM32_GPIO/UART`, `MODULE â†’ HAL`, `MODULE â†’ Register Access`, `MODULE â†’ CMSIS`, `MODULE â†’ FreeRTOS internals`, `PLATFORM â†’ MODULE`, `PLATFORM â†’ APP`, `BSP â†’ APP`. No circular dependencies.

### 7.3 Platform isolation rules
All MCU vendor files must reside inside `platform/<target>/` (e.g. `platform/stm32f407/`, `platform/esp32s3/`). Never place generated vendor code in project root. Forbidden at repo root: `/Core`, `/Drivers` â€” move into platform directory.

### 7.4 Interface rules
Every hardware service must expose an interface (e.g. `uart_if_t` with function pointers). Modules interact only with interfaces; must not know UART instance, GPIO port, DMA channel, MCU family.

### 7.5 Module rules
Each module owns one responsibility. Good: motor, imu, control, telemetry, storage. Bad: system_manager, all_in_one, utility, misc. Avoid god-modules.

### 7.6 RTOS separation
RTOS task creation belongs to `app/`; business logic belongs to `module/`. Pattern: `TASK â†’ MODULE API â†’ INTERFACE â†’ DRIVER`.

### 7.7 Architecture validation checklist
- [ ] Project follows required directory layout
- [ ] No HAL usage in `app/`
- [ ] No HAL usage in `module/`
- [ ] No register access outside `platform/`
- [ ] No CubeMX code outside `platform/`
- [ ] All peripherals abstracted through interfaces
- [ ] No circular dependencies
- [ ] No business logic inside BSP
- [ ] No business logic inside platform
- [ ] Modules have single responsibility
- [ ] Interfaces contain declarations only
- [ ] Dependency direction is correct

If violations found: report, explain harm, suggest corrected architecture, refactor.

