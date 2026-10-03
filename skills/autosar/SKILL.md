# autosar — AUTOSAR Classic / Adaptive capability (template replication 2)

Reusable AxiomEmbedded capability for AUTOSAR Classic Platform software
components, Adaptive Platform applications, and Classic↔Adaptive integration.

> Structure replicates the `mcu` template (see `docs/adr/0001-mcu-template.md`
> and `docs/adr/0003-autosar.md`). AUTOSAR work is safety-relevant: every
> software component must trace to an ISO 26262 work product.

## Objectives

- Develop Classic Platform SW-Cs (application layer, RTE, BSW services) against
  a pinned Classic release.
- Develop Adaptive Platform applications on `ara::com` (SOME/IP and DDS)
  against a pinned Adaptive release.
- Integrate and test Classic↔Adaptive communication (SOME/IP daemon pattern).
- Produce ISO 26262-6 software work products with full traceability.

## Prerequisites

- MCU + RTOS capabilities delivered (`skills/mcu/`, `skills/rtos/`).
- Pinned AUTOSAR release: Classic **R24-11** baseline (R25-11 current — verify
  before citing); Adaptive R24-11 baseline; Foundation R24-11.
- Toolchain: C++14-capable compiler for Adaptive (`ara` API per [RS_AP_00114]);
  C compiler with MISRA C:2025 for Classic.
- Domain overlay loaded: `domains/automotive/` (mandatory for this skill).

## Outcomes

- `requirements/autosar-requirements.md` tracing SYS-xxx to ASW-xxx per platform.
- `architecture/autosar-architecture.md`: platform choice (Classic/Adaptive/mixed),
  layered software architecture, functional-cluster map, communication matrix.
- `src/` + `headers/` SW-Cs / Adaptive apps with Doxygen APIs, MISRA clean.
- `test/` with RTE-level tests, `ara::com` service tests, Classic↔Adaptive
  integration tests on SOME/IP.
- `build/` CMake project, zero warnings with `-Wall -Wextra -Werror` on gcc and clang.
- `evidence/` linking every claim to a standard clause and a test result.

## Time estimate

- Platform setup + architecture: 3–5 days. SW-C/app development: 5–10 days. Integration + verification: 5–10 days.

## Resources

- Classic Platform releases (current R25-11; past R24-11 → R20-11):
  `https://www.autosar.org/standards/classic-platform`
- Classic R24-11 layered software architecture (Doc ID 53):
  `https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf`
- Foundation R24-11 safety requirements, Classic + Adaptive (Doc ID 986):
  `https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_RS_Safety.pdf`
- Adaptive R23-11 general requirements incl. C++14 API [RS_AP_00114]:
  `https://www.autosar.org/fileadmin/standards/R23-11/AP/AUTOSAR_AP_RS_General.pdf`
- SOME/IP protocol, Foundation R22-11 (Doc ID 696):
  `https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_SOMEIPProtocol.pdf`
- Adaptive Platform overview: `https://www.autosar.org/standards/adaptive-platform`
- MISRA C++:2023 (C++17 subset; Adaptive uses C++14 API — apply the stricter of the two).

## Platform choice guide

| Option | Use when |
| --- | --- |
| Classic (R24-11) | Hard real-time ECUs, signal-based CAN/LIN communication, static configuration, ASIL-D |
| Adaptive (R24-11) | High-performance MPUs (>20k DMIPS), service-oriented Ethernet (100 Mbps–1 Gbps), OTA updates, dynamic deployment |
| Mixed | Classic real-time control + Adaptive perception/compute, bridged via SOME/IP |

## Classic rules

- Layered architecture only: Application → RTE → Services → ECU Abstraction →
  MCAL → hardware. No layer bypass except documented Complex Drivers.
- Static configuration, OSEK-derived OS scheduling; freedom-from-interference per
  ISO 26262-6 argued in `domains/automotive/`, evidenced here.
- MISRA C:2025 mandatory/required clean or formally deviated.

## Adaptive rules

- `ara` namespace discipline: exactly one namespace per functional cluster below `ara`.
- C++14-compatible public interfaces ([RS_AP_00114]); error handling harmonized
  (communication errors merged to general `ara::com` communication error).
- SOME/IP and DDS for service communication with Classic, ROS, and peers.
- Apply MISRA C++:2023 where it exceeds the C++14 guidelines; record deltas.

## Integration and test strategy

- SOME/IP daemon pattern: Classic server ECU + Adaptive client ECU + daemon,
  so communication-method changes never touch application code.
- RTE-level and `ara::com` service tests on host; timing and bus-load tests on target.
- Coverage targets from `configs/skill-update.yaml`; ASIL C–D MC/DC required.
- Fault injection (`skills/fault-injection/`): lost daemon connection, link down,
  IPC corrupt, buffer overflow — each must resolve to the specified error path.

## Traceability

- `traceability-matrix.schema.json`: every SYS-xxx → ASW-xxx → `src/` file → `test/` case → evidence id.
- AUTOSAR specification items referenced by document ID + release (e.g. Doc ID 53, R24-11).

## Compliance mapping (via domain overlays, not duplication)

- Automotive: ISO 26262:2018 Parts 1–10 incl. Part 6 software; ASIL A–D.
- Foundation safety requirements (Doc ID 986) as the AUTOSAR-side argument input.
- Never claim certification from this heuristic skill — produce audit-ready evidence only.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill autosar` → PASS.
2. CMake configure + build, gcc and clang, zero warnings.
3. RTE/service/integration tests green at the required coverage.
4. MISRA scan clean or deviated with rationale; C++14 compatibility verified for Adaptive.
5. Traceability matrix complete; standards cited with number + version + clause + URL + document ID.
6. Safety deltas flagged for human review before PR (safety-relevant).

Load task-specific domain/platform/rule overlays before execution.
