---
name: architecture
description: System/software architecture views, interface contracts, allocation, and evaluation. Use when structuring a system, defining ICDs/APIs, or reviewing layering.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Architecture skill

System and software architecture for embedded and cyber-physical systems:
views, interface contracts, allocation to hardware/software, and the
architecture evaluation that proves the design satisfies its requirements
before implementation commits cost.

## 1. Purpose and scope

**Purpose.** Define a coherent structure — components, interfaces, behavior,
and allocation — that satisfies functional, timing, safety, security, and
resource requirements with recorded rationale.

**In scope.** Architecture views (functional, logical, technical, deployment),
interface definition (APIs, protocols, ICDs), allocation to HW/SW, reference
architectures (AUTOSAR Classic layering, ROS 2 graphs, layered Linux BSP),
architecture evaluation (ATAM-style trade analysis, prototyping of risks), and
ADRs for significant decisions.

**Non-goals.** Detailed design of individual units (see `implementation`) and
project scheduling. Ends at an evaluated, baselined architecture with ADRs.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 42010 Architecture description | 2022 (3rd ed.) | Viewpoints, views, correspondence rules, ADRs as rationale records | `https://www.iso.org/standard/50508.html` |
| 2 | ISO/IEC/IEEE 15288 System life cycle | 2023 | Architecture definition process, allocation and interface management | `https://www.iso.org/standard/81702.html` |
| 3 | AUTOSAR Classic layered architecture | R24-11 verified baseline (Doc ID 53); R25-11 current | BSW/RTE/Application layering rules | `https://www.autosar.org/standards/classic-platform/` |
| 4 | ISO 26262-4 System level | 2018 | Technical safety concept, system architectural design, ASIL allocation | `https://www.iso.org/standard/68386.html` |

## 3. View discipline

Produce exactly the views the system needs — no more, no fewer — but never
fewer than these four for anything above QM:

1. **Functional/logical.** Components and data/control flow answering "what
   does what"; maps 1:1 to system requirements (`requirements` §4).
2. **Technical/software.** Tasks, processes, middleware, OS assignment (RTOS
   tasks per `rtos`, Linux services per `embedded-linux`, ROS nodes per
   `robotics`); timing budgets attached per path.
3. **Deployment/hardware.** Allocation to MCU/MPU/SoC, buses, memories, power
   domains; resource budgets (flash, RAM, CPU, bandwidth) with margin policy
   (≥20% at architecture freeze is the default bar).
4. **Interface view.** Every cross-component interface specified: signatures,
   protocols, timing contracts, error behavior, versioning. Unspecified
   interfaces are the top architecture defect class — hunt them in review.

## 4. Architecture rules

1. **Layering enforced.** Application logic never touches registers, drivers
   never embed policy (HAL boundary per `mcu` §6, BSW/RTE per `autosar`).
2. **Freedom from interference by construction.** Mixed-criticality functions
   are partitioned in space (MPU/MMU) and time (schedule slots) at
   architecture level — see `safety` §5, `rtos` §5.
3. **Error model explicit.** Each interface documents failure modes, detection,
   and handling (return codes, safe states, retries with bounds); "cannot
   fail" is not an error model.
4. **Decisions recorded as ADRs.** Any decision affecting safety, security,
   timing, portability, or cost gets an ADR with context, options, decision,
   and consequences — stored with the architecture, not in chat history.
5. **Risks prototyped.** Top technical risks (new bus, new NPU, unproven RT
   path) are retired by spike prototypes with measured results before detailed
   design — the prototype report is architecture evidence.

## 5. Baselining gates (blocking)

1. All four views present and mutually consistent (correspondence per 42010).
2. Every interface specified with error model and versioning.
3. Resource budgets close with margin; timing budgets allocated per path.
4. Safety/security allocations trace to `safety`/`security` requirements.
5. ADRs recorded for all significant decisions; top risks retired by prototype.

## 6. Verification of this skill (Phase 4 gate)

- Architecture claims trace to requirements via the traceability matrix.
- No implementation starts on an unevaluated architecture (§5).
