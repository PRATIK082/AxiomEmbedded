---
name: safety
description: Functional-safety lifecycle with ASIL/SIL/DAL mapping, HARA chains, and sign-off gates. Use for safety goals, integrity levels, or safety cases.
version: 1.2.0
domains: [generic-embedded, automotive, aerospace, defense, industrial, robotics]
platforms: [all]
---

# Safety skill

Generic functional-safety engineering for embedded and cyber-physical systems.
Maps safety integrity levels to requirements, architecture, implementation,
verification, and safety-case work products across automotive, industrial,
aerospace, and robotics programs.

## 1. Purpose and scope

**Purpose.** Provide a repeatable V-model safety lifecycle that takes a product
from hazard analysis to an assessable safety case with full bidirectional
traceability.

**In scope.** Hazard analysis (HARA/HAZOP), integrity-level determination and
decomposition (ASIL/SIL/DAL), safety requirements derivation (FSR/TSR/SwSR),
safety mechanisms and architectures, tool qualification, verification
(FMEA/FTA/fault injection), and safety-case assembly.

**Non-goals.** This skill does not replace a certified assessor's judgement,
does not grant certification, and does not contain proprietary normative text
from any standard. Every claim below cites the standard's number, version, and
clause with a verifiable source.

**How to use.** Start at §3 (integrity level), derive requirements per §4,
select mechanisms per §5, verify per §6, and assemble evidence per §7.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Clause / part | Source |
|---|----------|------------------|---------------|--------|
| 1 | ISO 26262 Road vehicles — Functional safety | 2nd edition 2018, all 12 parts; Edition 3 in DIS (committee stage, not citable as released) | Part 3 concept, Part 4 system, Part 5 hardware, Part 6 software, Part 7 production/operation, Part 8 supporting processes, Part 9 ASIL decomposition, Part 11 semiconductors | `https://www.iso.org/standard/68383.html` |
| 2 | IEC 61508 Functional safety E/E/PE | Edition 2.0 (2010, all 7 parts), consolidated versions through 2024 | Parts 1–3 lifecycle/requirements, SIL 1–4 targets | `https://webstore.iec.ch/en/publication/5515` |
| 3 | RTCA DO-178C Software considerations in airborne systems | 2011-12-13, current | §12 tool qualification, Annex A objectives by DAL A–E | `https://www.rtca.org/products/software-considerations-in-airborne-systems-and-equipment-certification-do-178/` |
| 4 | RTCA DO-254 Design assurance for airborne electronic hardware | 2000-04-19, current | Design assurance levels A–E with hardware lifecycle objectives | `https://www.rtca.org/products/design-assurance-guidance-for-airborne-electronic-hardware-do-254/` |
| 5 | RTCA DO-330 Software tool qualification | 2011-12-13, current | TQL-1…TQL-5 vs DAL mapping | `https://www.rtca.org/products/software-tool-qualification-considerations-do-330/` |
| 6 | ISO 26262-8 Supporting processes | 2018 | Clause 11 qualification of software tools (TCL × use-case → ASCL) | `https://www.iso.org/standard/68390.html` |
| 7 | ISO 26262-5 Hardware level | 2018 | Clauses 8–9 hardware metrics SPFM/LFM, dependent-failure analysis | `https://www.iso.org/standard/68387.html` |

> Version note. ISO 26262:2018 is the citable release. References to "Edition 3"
> describe draft scope only (motorcycles, trucks/buses, semiconductors) until
> publication; never verify against a draft.

## 3. Integrity levels — determination and decomposition

### 3.1 Automotive (ISO 26262): ASIL A–D + QM

HARA (Part 3) rates each hazardous event on Severity (S0–S3), Exposure (E0–E4),
and Controllability (C0–C3); the S×E×C matrix yields QM or ASIL A (lowest) to
ASIL D (highest). The ASIL then drives every downstream rigor: methods required
per part, coverage targets, independence of verification, and confirmation
measures (Part 2 §6, Part 8 §6).

### 3.2 Industrial (IEC 61508): SIL 1–4

SILs map to probabilistic targets: SIL 1 ≥1e-2…SIL 4 ≥1e-5 dangerous failures
per demand (low-demand mode), or per-hour equivalents in continuous mode
(IEC 61508-1 §7.6). SIL 4 is reserved for the highest-risk functions and
implies the strictest architectural and systematic-capability constraints.

### 3.3 Airborne (DO-178C / DO-254): DAL A–E

DAL A (catastrophic) requires all 71 Annex A objectives with independence;
objectives shrink through DAL E (no safety effect, objectives informational).
Hardware follows the parallel DAL scale in DO-254.

### 3.4 Cross-domain mapping (planning aid, not a certification claim)

| Automotive | Industrial | Airborne SW | Airborne HW | Typical rigor signal |
|------------|-----------|-------------|-------------|----------------------|
| QM | — | DAL E | Level E | Standard quality management |
| ASIL A | SIL 1 | DAL D | Level D | Basic systematic process |
| ASIL B | SIL 2 | DAL C | Level C | Structured V&V, some independence |
| ASIL C | SIL 3 | DAL B | Level B | Independence, MC/DC recommended |
| ASIL D | SIL 4 | DAL A | Level A | Independence, MC/DC required, formal methods recommended |

### 3.5 Decomposition (ISO 26262-9 §5)

An ASIL D requirement may decompose into two independent ASIL B(D) requirements
**only if** independence (freedom from common cause, cascading, and dependent
failures) is demonstrated and each leg is developed to its decomposed level.
Document the decomposition, the independence argument, and the allocation in
the traceability matrix (`schemas/traceability-matrix.schema.json`).

## 4. Safety requirements chain (HARA → FSR → TSR → SwSR)

1. **Hazard analysis.** HARA (automotive, Part 3) or HAZOP/FTA/FMEA equivalents
   produce hazardous events with S/E/C ratings.
2. **Safety goals.** One top-level goal per hazardous event, with its ASIL/SIL/DAL
   and safe-state definition. Goals must be verifiable and technology-neutral.
3. **Functional safety requirements (FSR).** System-level requirements allocated
   to E/E architecture (Part 4), each inheriting an ASIL with rationale.
4. **Technical safety requirements (TSR).** Refine FSRs into hardware/software
   allocations with fault-tolerant time interval (FTTI), safe states, and
   diagnostic coverage targets.
5. **Software safety requirements (SwSR).** Unit-verifiable software requirements
   (Part 6 §6) traced to architecture, code, and tests — the backbone of
   `schemas/traceability-matrix.schema.json`.

Every link carries: ID, ASIL/SIL/DAL, safe state, FTTI where applicable,
verification method, and evidence pointer. Untraced safety requirements are a
blocking nonconformity.

## 5. Safety mechanisms and architectures

Select mechanisms to meet the diagnostic-coverage and freedom-from-interference
targets of the allocated level:

- **Supervision.** Independent watchdog (windowed), program-flow monitoring,
  clock/voltage monitors, lockstep cores (e.g. Cortex-R / ASIL-D MCUs).
- **Data integrity.** End-to-end CRC, redundant storage with comparison,
  plausibility checks on sensor inputs, control-flow signatures.
- **Freedom from interference.** MPU/MMU partitioning (see `mcu` §5, `rtos` §5),
  time partitioning (ARINC-653 style or static-cyclic schedules), WCET-bounded
  tasks so low-criticality load cannot starve safety functions.
- **Safe states.** Defined de-energized/limp-home/fail-silent states with
  transition time ≤ FTTI; every safety goal names its safe state.
- **Hardware metrics (ISO 26262-5).** Single-point fault metric (SPFM) and
  latent-fault metric (LFM) targets per ASIL: ASIL D SPFM ≥ 99%, LFM ≥ 90%;
  ASIL C SPFM ≥ 97%, LFM ≥ 80%; ASIL B SPFM ≥ 90%, LFM ≥ 60%. Verify by FMEDA.

## 6. Verification and confirmation measures

| Activity | ASIL A/B signal | ASIL C/D signal | Reference |
|----------|-----------------|-----------------|-----------|
| Requirements reviews / inspections | Required | Required + independent | 26262-6 §6, 26262-8 §6 |
| Structural coverage | Statement + branch 100% | + MC/DC 100% at ASIL D | `configs/skill-update.yaml` |
| Fault injection (HW/SW) | Sampled | Systematic per FTTI/safe-state claim | 26262-5 §9, 26262-6 §9 |
| FMEA / FTA | FMEA | FMEA + FTA + dependent-failure analysis | 26262-8, 61508-7 |
| Back-to-back / MIL-SIL-HIL | Recommended | Required evidence chain | `validation` skill |
| Tool qualification | TCL1/ASCL-A minimal | TCL3 tools qualified to TQL/ASCL per use case | 26262-8 §11, DO-330 |
| Confirmation reviews | Functional-safety audit | + Independent safety assessment | 26262-2 §6 |

## 7. Work products, evidence, and sign-off gates

**Work products.** Safety plan, HARA/HAZOP report, safety goals, FSR/TSR/SwSR
specifications, architecture with independence argument, FMEDA, V&V reports,
tool-qualification reports, safety case, assessment report.

**Evidence schema.** Record tool qualification, coverage, fault-injection
results, and assessment outcomes in `schemas/compliance-evidence.schema.json`
(`tool_qualification`, `objectives_table`, `deviations`).

**Sign-off gates (blocking, human approval required).**

1. HARA complete, safety goals assigned integrity levels with rationale.
2. FSR/TSR/SwSR traceability chain gap-free in the traceability matrix.
3. Architecture independence argument accepted (decomposition valid).
4. Coverage targets met per allocated level; MC/DC at ASIL D documented.
5. Fault-injection campaign covers every safe-state transition.
6. Independent safety assessment recorded with disposition of all findings.

## 8. Verification of this skill (Phase 4 gate)

- All seven normative sources carry number + version + clause + URL (§2).
- Integrity-level tables map ASIL/SIL/DAL without claiming equivalence certification.
- Coverage and traceability rules in `rules/skill-update-gates.yaml` enforced.
- Safety-sensitive content → `verify_skill.py` flags human review; no
  safety-significant release proceeds without a recorded human approval.
