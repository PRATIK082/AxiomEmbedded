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
