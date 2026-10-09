---
name: automotive-vcycle
description: End-to-end automotive V-Cycle lifecycle from stakeholder requirements to vehicle validation. Use for V-Model planning, MIL/SIL/HIL gates, ASPICE/ISO 26262 alignment, or agile-hybrid programs.
version: 1.2.0
domains: [automotive]
platforms: [all]
---

# automotive-vcycle — Advanced automotive V-Cycle / V-Model lifecycle

Reusable AxiomEmbedded lifecycle skill covering the full automotive V-Model:
left-arm decomposition (requirements → architecture → design → implementation),
right-arm integration and validation (unit → integration → system → vehicle),
with MIL/SIL/HIL/PIL gates, ASPICE + ISO 26262 alignment, and agile-hybrid execution.

> Lifecycle policy: `configs/project.yaml` declares `v-model` as default.
> This skill is the automotive instantiation. Standards **metadata only** —
> no proprietary normative text. Produces audit-ready evidence; never grants certification.

## Objectives

- Plan and execute a complete left-arm → right-arm V-Cycle with explicit
  entry/exit criteria at every gate.
- Align each V leg to ASPICE (SYS/SWE) and ISO 26262 (Parts 3/4/6/8) work products.
- Operate MIL/SIL/HIL/PIL/vehicle environments as a staged evidence chain.
- Run the V in an agile-hybrid cadence (sprints feed V legs; PIs close V gates).
- Enforce defect/change loopback discipline and bidirectional traceability.

## Prerequisites

- AxiomEmbedded repo conventions loaded: `README.md`, `REPOSITORY_INVENTORY.md`,
  `docs/agents/working-agreement.md`, `configs/project.yaml`.
- Companion skills as needed: `safety`, `autosar`, `mcu`/`rtos`, `validation`.
- Pinned baselines: ASPICE PAM version, ISO 26262:2018 edition.
- Requirement/test tooling with stable IDs and traceability schema.

## Outcomes

- `requirements/` — stakeholder, system, software requirements with ASIL + verification method.
- `architecture/` — system + software architecture with ICD, FTTI/safe-state allocation.
- `src/` + `headers/` — implemented units per detailed design, MISRA-governed.
- `test/` — unit, integration, qualification, system, vehicle test specs and results.
- `evidence/` — MIL/SIL/HIL/PIL/vehicle reports, coverage, gate records.
- `traceability-matrix` — gap-free bidirectional chain; gate sign-offs.

## Time estimate

- V planning + SYS.1/SYS.2: 1–2 weeks. SYS.3/SWE.1/SWE.2: 2–4 weeks.
- SWE.3 + SWE.4/SWE.5: 3–8 weeks per release train. SWE.6/SYS.4/SYS.5 + vehicle: 2–6 weeks.

## Resources

| # | Topic | Source |
|---|-------|--------|
| 1 | ISO 26262 series overview (2nd ed. 2018) | `https://www.iso.org/standard/68383.html` |
| 2 | ISO 26262-8 supporting processes | `https://www.iso.org/standard/68390.html` |
| 3 | Automotive SPICE PAM/PRM | `https://www.automotivespice.com/` |
| 4 | INCOSE SE Handbook (V-model) | `https://www.incose.org/products-and-publications/se-handbook` |
| 5 | ISTQB Foundation syllabus | `https://www.istqb.org/certifications/certified-tester-foundation-level` |

## Left-arm practices

### SYS.1 — Stakeholder / concept
Entry: item definition draft. Practices: elicit needs; define boundary, modes,
misuse; draft validation targets. Exit: baselined StkR-xxx with validation method.

### SYS.2 — System requirements + FSR
Derive verifiable SYS-xxx; allocate FSRs with ASIL; assign FTTI/safe state;
define verification method at authoring time. Exit: SYS-xxx baselined, 100% traced to StkR.

### SYS.3 — System architecture + TSR
Decompose into subsystems/ECUs/signals; define TSRs; fix interfaces; argue
freedom from interference; record ADRs. Exit: architecture + ICD; integration strategy drafted.

### SWE.1 — Software requirements + SwSR
Atomic, testable SwSR-xxx inheriting ASIL with timing/resource constraints.
Exit: SwSR baselined; each names its test level.

### SWE.2 — Software architecture
Components, layering, concurrency, safety mechanisms; trace + review.
Exit: architecture + interface specs; SwSR→component trace complete.

### SWE.3 — Detailed design + construction
Detailed design for ASIL C/D before coding; static analysis + review mandatory.
Exit: code + design reviewed, statically clean, trace-tagged.

Agile-hybrid: sprints produce increments; Definition of Ready/Done = entry/exit
criteria; each PI ends with a gate review.

## Right-arm verification mapping

| # | Left-arm | Right-arm | Method | Environment | Entry | Exit |
|---|----------|-----------|--------|-------------|-------|------|
| 1 | SWE.3 | SWE.4 unit verification | Static + dynamic unit test; MC/DC at ASIL D | Host / SIL | Code reviewed; stubs ready | 100% pass; coverage met |
| 2 | SWE.2 | SWE.5 SW integration | Interface/sequence, fault injection at API | SIL → HIL | Interfaces frozen | All interfaces exercised incl. error paths |
| 3 | SWE.1 | SWE.6 SW qualification | Requirements-based functional + robustness | SIL / HIL | SwSR baselined; env calibrated | Every SwSR verified; regression baselined |
| 4 | SYS.3 | SYS.4 system integration | E2E signal/service, bus-load, FTTI measurement | HIL | ICD frozen; HIL models validated | FTTI/safe-state evidenced on HIL |
| 5 | SYS.2/SYS.1 | SYS.5 qualification + vehicle | Acceptance drives, scenario catalog | HIL + vehicle | SYS.4 passed; vehicle ready | Validation targets met |

Back-to-back rule: same vectors on MIL and SIL where both exist; unexplained
divergence blocks HIL entry.

## MIL / SIL / HIL / PIL / vehicle strategy

| Environment | What runs | Gate role |
|-------------|-----------|-----------|
| MIL | Control/plant models | Pre-code confidence |
| SIL | Compiled target code on host/virtual ECU | SWE.4/SWE.5/SWE.6 primary; coverage measured |
| PIL | Target binary on real MCU/MPU | Required when timing/footprint claimed |
| HIL | Real ECUs + simulated plant/bus/faults | SYS.4 primary evidence |
| Vehicle | Full system in real environment | SYS.5 only; never substitutes failed HIL |

Promote strictly upward MIL→SIL→PIL→HIL→vehicle. Freeze and version every
artifact affecting results. Re-run full regression on calibration/compiler/model/bus-DB change.

## Change / defect loopback rules (blocking)

1. No right-arm-only fixes — loop back to left arm first, then re-verify upward.
2. Impact analysis mandatory per change: affected IDs, ASIL impact, regression scope.
3. Critical/major defects block promotion; minor may defer with dated action.
4. Any baselined change triggers regression; results appended, never overwritten.
5. Vehicle anomalies map to requirement/architecture/implementation/rig cause.
6. Follow ASPICE SUP.9/SUP.10 + ISO 26262-8 §8 change management.

## Traceability

- Chain: `StkR → SYS → TSR/SwSR → component/file → test case → result → evidence id`.
- Every requirement: ID, ASIL, safe state/FTTI, verification method, environment, evidence pointer.
- Blocking gaps: untraced requirement, untested ASIL requirement, test without
  environment versions, result without evidence pointer.

## Compliance mapping

| Artifact | ASPICE | ISO 26262 |
|----------|--------|-----------|
| Stakeholder requirements | SYS.1 | 26262-3 item/validation input |
| System requirements + FSR | SYS.2 | 26262-4 §6 |
| System architecture + TSR | SYS.3 | 26262-4 §7 |
| Software requirements | SWE.1 | 26262-6 §6 |
| Software architecture | SWE.2 | 26262-6 §7 |
| Design + code | SWE.3 | 26262-6 §8 |
| Unit / integration | SWE.4 / SWE.5 | 26262-6 §9 |
| Qualification / system | SWE.6 / SYS.4-5 | 26262-4 §8 |

Cite number + version + clause + URL. Never claim capability levels or ASIL
compliance from heuristic checks.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill automotive-vcycle` → PASS.
2. Left-arm baselines gap-free in traceability matrix.
3. Right-arm mapping instantiated with method, environment, entry/exit criteria.
4. MIL/SIL deltas closed; HIL models versioned; vehicle results linked.
5. Coverage targets met per ASIL; deviations formally recorded.
6. Zero right-arm-only fixes; regression re-run recorded.
7. No certification language present.
8. Human gate approval for SYS.3, SWE.2, SYS.4, SYS.5 recorded.

Load task-specific domain/platform/rule overlays before execution.
