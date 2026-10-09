---
name: automotive-diagnostics
description: UDS/DoIP/OBD-II/J1939/XCP diagnostics, tester integration (ODX/OTX), DTC/DID/routine control, security access. Use for diagnostic stacks, FBL testers, or homologation evidence.
version: 1.2.0
domains: [automotive]
platforms: [mcu, mpu, autosar-classic, autosar-adaptive]
---

# automotive-diagnostics — Vehicle diagnostics and tester capability

Reusable AxiomEmbedded capability for on-vehicle diagnostic servers (UDS, OBD-II/WWH-OBD,
J1939, XCP slave) and off-vehicle testers (ODX/OTX-driven), including flash-bootloader (FBL)
programming flows, DTC/DID/routine management, session control, security access, and SecOC
interaction points.

## Objectives

- Implement a UDS server per ISO 14229-1 service matrix with correct session, addressing,
  and negative-response behaviour.
- Expose DoIP (ISO 13400) discovery, routing activation, and diagnostic transport for Ethernet ECUs.
- Support legislated OBD-II/WWH-OBD alongside UDS without DID/DTC semantic collision.
- Support J1939 diagnostics (DM1/DM2/DM3, address-claim awareness) and XCP slave behaviour.
- Drive the ECU from an ODX/OTX-based tester (ISO 22901) and prove the FBL sequence end to end.
- Manage DTCs, DIDs, routines, and I/O control with full traceability.

## Prerequisites

- MCU/RTOS or AUTOSAR capability delivered (`skills/mcu/`, `skills/autosar/`).
- Transport available: CAN/CAN-FD (`skills/automotive-networks/`) and/or DoIP/Ethernet;
  bootloader slot discipline (`skills/bootloader/`).
- Pinned baselines recorded (verify before citing): ISO 14229-1:2020, ISO 13400-2:2019,
  ISO 15031 series, SAE J1979, SAE J1939-73, ASAM MCD-1 XCP, ISO 22901-1 (ODX), ISO 22901-3 (OTX).
- Domain overlay loaded: `domains/automotive/` (mandatory).

## Outcomes

- `requirements/diagnostic-requirements.md`: service/DID/DTC/routine catalogue with
  session/security preconditions per item.
- `architecture/diagnostic-architecture.md`: server/tester split, transport mapping, ODX chain, FBL handover.
- `src/` diagnostic server (session layer, service dispatch, DID/DTC store, security-access hooks).
- `test/` positive/negative service tests, session-transition tests, NRC coverage, tester regression pack.
- `evidence/` linking every service/NRC/DTC claim to standard identifier + test result.

## Time estimate

- Server skeleton + service matrix: 3–5 days. DoIP/tester/FBL integration: 5–8 days.
  Negative-path + security-access hardening and evidence: 3–5 days.

## Resources (public landing pages only — no normative text)

- ISO 14229 landing: `https://www.iso.org/search.html?q=14229`
- ISO 13400 landing: `https://www.iso.org/search.html?q=13400`
- ISO OBP: `https://www.iso.org/obp/ui`
- ASAM ODX: `https://www.asam.net/standards/detail/mcd-2-d/`
- ASAM XCP: `https://www.asam.net/standards/detail/mcd-1-xcp/`
- ASAM overview: `https://www.asam.net/standards/`
- SAE J1979: `https://www.sae.org/search/?q=J1979`
- OPEN Alliance: `https://www.opensig.org/`

## Rule 1 — UDS service matrix (identifiers only)

| SID | Name | Typical use | Session gate |
| --- | ---- | ----------- | ------------ |
| 0x10 | DiagnosticSessionControl | default/extended/programming | always allowed |
| 0x11 | ECUReset | hard/soft reset | extended or programming |
| 0x19 | ReadDTCInformation | status, snapshot, extended data | default+ (project pins subfunctions) |
| 0x22 | ReadDataByIdentifier | DID read | per-DID session/security |
| 0x23 | ReadMemoryByAddress | memory read (restrict in production) | extended + secured |
| 0x27 | SecurityAccess | seed/key unlock | session-specific levels |
| 0x28 | CommunicationControl | enable/disable normal comm | extended or programming |
| 0x2E | WriteDataByIdentifier | DID write/variant coding | extended + secured |
| 0x2F | InputOutputControlByIdentifier | actuator override | extended + secured, timeout-guarded |
| 0x31 | RoutineControl | start/stop/results | per-routine gate |
| 0x34–0x38 | RequestDownload/TransferData/Exit (+Upload) | FBL data transfer | programming only + secured |
| 0x85 | ControlDTCSetting | DTC on/off | extended or programming |

Rules: unknown SID → NRC 0x11; unsupported subfunction → NRC 0x12; wrong session → NRC
0x7F context; secured resource without unlock → NRC 0x33. Suppressible responses honour
the subfunction MSB; functional addressing never returns NRCs on the bus.

## Rule 2 — NRC handling table (identifiers only)

| NRC | Name | Mandatory behaviour |
| --- | ---- | ------------------- |
| 0x11 | serviceNotSupported | unknown SID in session |
| 0x12 | subFunctionNotSupported | unsupported subfunction |
| 0x13 | incorrectMessageLengthOrInvalidFormat | length/format guard first |
| 0x22 | conditionsNotCorrect | state/voltage/speed interlock |
| 0x24 | requestSequenceError | e.g. TransferData before RequestDownload |
| 0x31 | requestOutOfRange | unknown DID/DTC/routine/memory window |
| 0x33 | securityAccessDenied | locked resource accessed |
| 0x35 | invalidKey | failed seed/key, attempt counter++ |
| 0x36 | exceedNumberOfAttempts | lockout timer, auditable event |
| 0x37 | requiredTimeDelayNotExpired | seed request during lockout |
| 0x72 | generalProgrammingFailure | erase/write failure in FBL |
| 0x78 | responsePending | long routine/erase; S3 kept alive |
| 0x7E | subFunctionNotSupportedInActiveSession | right function, wrong session |
| 0x7F | serviceNotSupportedInActiveSession | right service, wrong session |

Evaluate in fixed order: format → session → security → conditions → resource → execution.
Log every negative path; a service with only positive-path tests is incomplete.

## Rule 3 — Session, security-access, and SecOC posture

1. **Sessions:** default (safe subset), extended (workshop/test), programming (FBL exclusive,
   normal communication off, DTCs off). S3 timeout returns to default; timeout value is a
   requirement, not a constant.
2. **Security access:** seed/key per level; one level per protected domain minimum.
   Failed attempts → delay + NVM counter; lockout is tested, not asserted. Production keys
   never in source; test keys flagged `TEST-ONLY` and blocked by build gate.
3. **SecOC:** diagnostic unlock does not bypass SecOC; secured PDUs still require freshness/MAC.
4. **OBD vs UDS:** legislated OBD stays available per regulation in default session;
   manufacturer UDS stays gated. J1939 DM coexists without redefining UDS DTC bytes.

## Rule 4 — Tester (ODX/OTX) and FBL chain

1. ODX (ISO 22901-1) is the single source of DID/DTC/com-param definitions; generated tester
   data identifies its ODX source and version. No hand-typed DID tables in tester code.
2. OTX (ISO 22901-3) owns the FBL flow: session → security → routine(erase) → download →
   transfer → exit → checksum routine → reset. Each step asserts expected response.
3. XCP (where fitted) is calibration/measurement only; reprogramming goes through UDS/FBL.
   XCP and UDS resource locks are mutually exclusive and tested as such.

## Integration and test strategy

- Service-matrix pack: every SID x session x locked/unlocked x functional/physical,
  asserting the exact NRC on failure.
- Tester-in-the-loop: ODX-driven regression on simulated and real ECU; DoIP denial and S3 cases.
- FBL campaign: download → verify → boot trial image; power-loss at erase/transfer/exit each
  leaves a bootable image (with `skills/bootloader/` matrix).
- Security tests: wrong-key, attempt-exhaustion, lockout-timing, downgrade rejection;
  SecOC-failure injection where SecOC is on.

## Traceability

- Requirement → SID/DID/DTC/routine → `src/` handler → `test/` case → ODX element → evidence id.
- Standards cited as number + version + identifier only with landing URL.

## Compliance mapping (via overlays, not duplication)

- ISO 26262:2018 (diagnostic faults as safety mechanisms where claimed);
  ISO/SAE 21434 (security-access, key management, TARA linkage); UNECE R155/R156 touchpoints.
- Emissions/OBD regulation applicability recorded project-side. Never claim type approval.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill automotive-diagnostics` → PASS.
2. Service-matrix pack green; every NRC in Rule 2 hit at least once.
3. Session-timeout, lockout-timing, FBL power-loss cases demonstrated.
4. ODX source/version recorded for all generated tester data.
5. Test keys absent from production build; lockout counters in NVM proven.
6. Traceability complete; no copied normative text.
7. Safety/security deltas flagged for human review before PR.

Load task-specific domain/platform/rule overlays before execution.
