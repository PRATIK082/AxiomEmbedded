---
name: automotive-diagnostics
description: UDS/DoIP/OBD-II/J1939/XCP diagnostics, tester integration (ODX/OTX), DTC/DID/routine control, security access, AUTOSAR-extract-driven UDS test/validation codegen (DEXT/ARXML/ODX/CDD/XLS/YAML/JSON) with full service/subservice positive/negative coverage. Use for diagnostic stacks, FBL testers, diag test-tool creation, or homologation evidence.
version: 1.3.0
domains: [automotive]
platforms: [mcu, mpu, autosar-classic, autosar-adaptive]
---

# automotive-diagnostics — Vehicle diagnostics and tester capability

Reusable AxiomEmbedded capability for on-vehicle diagnostic servers (UDS, OBD-II/WWH-OBD,
J1939, XCP slave) and off-vehicle testers (ODX/OTX-driven), including flash-bootloader (FBL)
programming flows, DTC/DID/routine management, session control, security access, and SecOC
interaction points. This version adds extract-driven test/validation code generation and
tool-creation guidance: build a deterministic generator that ingests an AUTOSAR diagnostic
extract (or equivalent XLS/XLSX, ODX/PDX, CDD, YAML/JSON, OTX script set) and emits the full
per-service/per-subfunction positive + negative test matrix with traceability.

## Objectives

- Implement a UDS server per ISO 14229-1 service matrix with correct session, addressing,
  and negative-response behaviour (full SID/subfunction scope per Rule 1).
- Expose DoIP (ISO 13400) discovery, routing activation, and diagnostic transport for Ethernet ECUs.
- Support legislated OBD-II/WWH-OBD alongside UDS without DID/DTC semantic collision.
- Support J1939 diagnostics (DM1/DM2/DM3, address-claim awareness) and XCP slave behaviour.
- Drive the ECU from an ODX/OTX-based tester (ISO 22901) and prove the FBL sequence end to end.
- Manage DTCs, DIDs, routines, and I/O control with full traceability.
- Generate positive + negative test/validation code from a machine-readable diag extract,
  and ship the generator itself as a versioned, deterministic tool (Rules 5–7).

## Prerequisites

- MCU/RTOS or AUTOSAR capability delivered (`skills/mcu/`, `skills/autosar/`).
- Transport available: CAN/CAN-FD (`skills/automotive-networks/`) and/or DoIP/Ethernet;
  bootloader slot discipline (`skills/bootloader/`).
- Pinned baselines recorded (verify before citing): ISO 14229-1:2020 (Edition 4: 2026-06
  published — verify applicability before citing), ISO 13400-2:2019,
  ISO 15031 series, SAE J1979, SAE J1939-73, ASAM MCD-1 XCP, ISO 22901-1 (ODX), ISO 22901-3 (OTX),
  AUTOSAR Classic R24-11 (current R25-11 — verify), AUTOSAR Diagnostic Extract Template (DEXT).
- Domain overlay loaded: `domains/automotive/` (mandatory).
- Test/validation levels loaded as needed: `skills/unit-test/`, `skills/integration-test/`,
  `skills/system-test/`, `skills/test-automation/`, `skills/validation/`.

## Outcomes

- `requirements/diagnostic-requirements.md`: service/DID/DTC/routine catalogue with
  session/security preconditions per item.
- `architecture/diagnostic-architecture.md`: server/tester split, transport mapping, ODX chain, FBL handover.
- `src/` diagnostic server (session layer, service dispatch, DID/DTC store, security-access hooks).
- `test/` positive/negative service tests, session-transition tests, NRC coverage, tester regression pack —
  generated from the extract (Rule 6), never hand-typed from prose.
- `tools/<diag-testgen>/` deterministic generator (Rule 7) with manifest, schema, versioned output.
- `evidence/` linking every service/NRC/DTC claim to standard identifier + test result.

## Time estimate

- Server skeleton + service matrix: 3–5 days. DoIP/tester/FBL integration: 5–8 days.
  Negative-path + security-access hardening and evidence: 3–5 days.
- Extract ingestion + generator + golden vectors: 3–5 days (once; reused per ECU variant).

## Resources (public landing pages only — no normative text)

- ISO 14229 landing: `https://www.iso.org/search.html?q=14229`
- ISO 14229-1:2026 publication page: `https://committee.iso.org/standard/87962.html`
- ISO 13400 landing: `https://www.iso.org/search.html?q=13400`
- ISO OBP: `https://www.iso.org/obp/ui`
- ASAM ODX: `https://www.asam.net/standards/detail/mcd-2-d/`
- ASAM XCP: `https://www.asam.net/standards/detail/mcd-1-xcp/`
- ASAM overview: `https://www.asam.net/standards/`
- SAE J1979: `https://www.sae.org/search/?q=J1979`
- AUTOSAR Classic platform: `https://www.autosar.org/standards/classic-platform`
- AUTOSAR DEXT requirements (R24-11, Doc ID 681): `https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_RS_DiagnosticExtractTemplate.pdf`
- AUTOSAR diagnostic acceptance tests (Doc ID 627): `https://www.autosar.org/fileadmin/fileadmin/standards/tests/1-0/AUTOSAR_ATS_DiagnosticServices.pdf`
- UDS SID reference (community, cross-check against standard): `https://uds.readthedocs.io/en/latest/pages/knowledge_base/service.html`
- OPEN Alliance: `https://www.opensig.org/`

## Rule 1 — UDS service matrix, full scope (identifiers only)

Cover every request SID below for server dispatch AND test generation. "Cover" means: for each
SID the project declares supported / not-supported, and for each supported SID every
subfunction the extract lists, with one positive case per subfunction plus the negative cases
from Rule 2. Unsupported SIDs still get a negative test (NRC 0x11). Subfunction MSB (0x80)
is the suppress-positive-response (SPR) bit — test SPR=0 and SPR=1 where the service uses
subfunctions.

| SID | Name | Subfunctions / selectors in scope | Session gate (default) |
| --- | ---- | -------------------------------- | ---------------------- |
| 0x10 | DiagnosticSessionControl | 0x01 default, 0x02 programming, 0x03 extended, 0x40–0x7F vehicle-manufacturer, 0x60–0x7E system-supplier; SPR bit | always allowed |
| 0x11 | ECUReset | 0x01 hardReset, 0x02 keyOffOnReset, 0x03 softReset, 0x04 enableRapidPowerShutDown, 0x05 disableRapidPowerShutDown; SPR bit | extended or programming |
| 0x14 | ClearDiagnosticInformation | groupOfDTC (0x000000/0xFFFFFF + project groups); no subfunction | per project (default+ typical) |
| 0x19 | ReadDTCInformation | 0x01 reportNumberOfDTCByStatusMask, 0x02 reportDTCByStatusMask, 0x03 snapshotIdentification, 0x04 snapshotRecordByDTCNumber, 0x05 storedDataByNumber, 0x06 extDataRecordByDTCNumber, 0x07 numberOfDTCBySeverityMaskRecord, 0x08 DTCBySeverityMaskRecord, 0x09 severityMaskRecord, 0x0A reportSupportedDTC, 0x0B firstTestFailedDTC, 0x0C firstConfirmedDTC, 0x0D mostRecentTestFailedDTC, 0x0E mostRecentConfirmedDTC, 0x0F mirrorMemoryDTC*, 0x10 mirrorMemoryDTCStatusMask*, 0x11 numberOfMirrorMemoryDTCByStatusMask*, 0x12 numberOfEmissionsOBDDTCByStatusMask, 0x13 emissionsOBDDTCByStatusMask, 0x14 DTCFaultDetectionCounter, 0x15 DTCWithPermanentStatus, 0x16 DTCSeverityMaskRecord (with functional group), 0x17 longTermPrimaryODCTC*, 0x18 reportDTCPrimaryODCTC*, 0x19 functionalGroupIdentification*, 0x1A reportSupportedDTCWithPermanent*, 0x1B DTCFaultDetectionCounterWithAging*, 0x1C–0x41 ISO/SAE reserved (verify), 0x42 reportWWHOBDDTCByMaskRecord (AUTOSAR SRS_Diag_04139), 0x55 reportDTCWithPermanentStatusExtended* | default+ (project pins each subfunction) |
| 0x22 | ReadDataByIdentifier | DID list from extract (incl. 0xF1xx–0xF2xx identification/scaling ranges per project); no subfunction | per-DID session/security |
| 0x23 | ReadMemoryByAddress | addressAndLengthFormatIdentifier + memoryAddress + memorySize; no subfunction | extended + secured |
| 0x24 | ReadScalingDataByIdentifier | DID list (scaling records); no subfunction | per-DID session/security |
| 0x27 | SecurityAccess | 0x01/0x03/0x05… requestSeed (odd, per level), 0x02/0x04/0x06… sendKey (even); levels from extract (min. one per protected domain) | session-specific levels |
| 0x28 | CommunicationControl | 0x00 enableRxAndTx, 0x01 enableRxAndDisableTx, 0x02 disableRxAndEnableTx, 0x03 disableRxAndTx (+ 0x04–0xFF reserved/enhanced per project); communicationType bitmask; SPR bit | extended or programming |
| 0x29 | Authentication | 0x00 deAuthenticate, 0x01 verifyCertificateUnidirectional, 0x02 verifyCertificateBidirectional, 0x03 proofOfOwnership, 0x04 transmitCertificate, 0x05 requestChallengeForAuthentication, 0x06 verifyProofOfOwnershipUnidirectional, 0x07 verifyProofOfOwnershipBidirectional, 0x08 authenticationConfiguration; SPR bit | per project |
| 0x2A | ReadDataByPeriodicIdentifier | 0x01 slowRate, 0x02 mediumRate, 0x03 fastRate, 0x04 stopSending; transmissionMode + periodicDataIdentifier | extended typical |
| 0x2C | DynamicallyDefineDataIdentifier | 0x01 defineByIdentifier, 0x02 defineByMemoryAddress, 0x03 clearDynamicallyDefinedDataIdentifier | extended + secured typical |
| 0x2E | WriteDataByIdentifier | DID list from extract; no subfunction | extended + secured |
| 0x2F | InputOutputControlByIdentifier | DID + 0x00 returnControlToECU, 0x01 resetToDefault, 0x02 freezeCurrentState, 0x03 shortTermAdjustment; controlEnableMask + controlState | extended + secured, timeout-guarded |
| 0x31 | RoutineControl | 0x01 startRoutine, 0x02 stopRoutine, 0x03 requestRoutineResults; routineIdentifier + routineControlOptionRecord from extract | per-routine gate |
| 0x34 | RequestDownload | dataFormatIdentifier + addressAndLengthFormatIdentifier + memoryAddress + memorySize | programming only + secured |
| 0x35 | RequestUpload | same encoding as 0x34 | programming only + secured |
| 0x36 | TransferData | blockSequenceCounter + transferRequestParameterRecord | programming only + secured, after 0x34/0x35 |
| 0x37 | RequestTransferExit | transferRequestParameterRecord | programming only + secured, closes 0x36 sequence |
| 0x38 | RequestFileTransfer | 0x01 addFile, 0x02 deleteFile, 0x03 replaceFile, 0x04 readFile, 0x05 readDir, 0x06 resumeFile; filePathAndName + dataFormat | programming only + secured |
| 0x3D | WriteMemoryByAddress | addressAndLengthFormatIdentifier + memoryAddress + memorySize + dataRecord | extended + secured (restrict in production) |
| 0x3E | TesterPresent | 0x00 zeroSubFunction (keep-alive, SPR=1 typical); SPR bit | always allowed |
| 0x83 | AccessTimingParameter | 0x01 readExtendedTimingParameterSet, 0x02 setTimingParametersToDefaultValues, 0x03 readCurrentlyActiveTimingParameters, 0x04 setTimingParametersToGivenValues; SPR bit | extended typical |
| 0x84 | SecuredDataTransmission | no subfunction (wraps inner APDU) | per inner service |
| 0x85 | ControlDTCSetting | 0x01 on, 0x02 off (+ DTCSettingType / groups per project); SPR bit | extended or programming |
| 0x86 | ResponseOnEvent | 0x00 stopResponseOnEvent, 0x01 onDTCStatusChange, 0x02 onTimerInterrupt, 0x03 onChangeOfDataIdentifier, 0x04 reportActivatedEvents, 0x05 startResponseOnEvent, 0x06 clearResponseOnEvent, 0x07 onComparisonOfValues, 0x08–0xFF reserved/vehicle-manufacturer; storageState + windowTime + eventType records | extended typical |
| 0x87 | LinkControl | 0x01 verifyModeTransitionWithFixedParameter, 0x02 verifyModeTransitionWithSpecificParameter, 0x03 transitionMode; SPR bit | extended typical |

`*` = only where the extract/project enables it; generator must emit the case iff the subfunction
is declared supported, else emit the NRC 0x12 negative case. Manufacturer ranges (0x40–0x7F
subfunctions, 0xBA–0xBF SIDs) are project-declared in the extract — never invented by the tool.

Rules: unknown SID → NRC 0x11; unsupported subfunction → NRC 0x12; wrong session → NRC
0x7E/0x7F context (Rule 2); secured resource without unlock → NRC 0x33. Suppressible responses honour
the subfunction MSB; functional addressing never returns NRCs on the bus. Positive-response SID
is always request SID + 0x40; negative response is always `7F <SID> <NRC>`.

## Rule 2 — NRC handling table (identifiers only)

| NRC | Name | Mandatory behaviour |
| --- | ---- | ------------------- |
| 0x10 | generalReject | last-resort reject, auditable |
| 0x11 | serviceNotSupported | unknown/unsupported SID in session |
| 0x12 | subFunctionNotSupported | unsupported subfunction |
| 0x13 | incorrectMessageLengthOrInvalidFormat | length/format guard first |
| 0x21 | busyRepeatRequest | transient busy, retryable |
| 0x22 | conditionsNotCorrect | state/voltage/speed interlock |
| 0x24 | requestSequenceError | e.g. TransferData before RequestDownload |
| 0x31 | requestOutOfRange | unknown DID/DTC/routine/memory window |
| 0x33 | securityAccessDenied | locked resource accessed |
| 0x35 | invalidKey | failed seed/key, attempt counter++ |
| 0x36 | exceedNumberOfAttempts | lockout timer, auditable event |
| 0x37 | requiredTimeDelayNotExpired | seed request during lockout |
| 0x70 | uploadDownloadNotAccepted | 0x34/0x35/0x38 rejected (mode/length/format) |
| 0x71 | transferDataSuspended | 0x36 suspended, resumable per project |
| 0x72 | generalProgrammingFailure | erase/write failure in FBL |
| 0x73 | wrongBlockSequenceCounter | 0x36 counter mismatch |
| 0x78 | requestCorrectlyReceivedResponsePending | long routine/erase; S3 kept alive, final response follows |
| 0x7E | subFunctionNotSupportedInActiveSession | right function, wrong session |
| 0x7F | serviceNotSupportedInActiveSession | right service, wrong session |

Evaluate in fixed order: format (0x13) → session (0x7E/0x7F) → security (0x33/0x35/0x36/0x37)
→ conditions (0x22) → resource (0x11/0x12/0x31) → sequence (0x24/0x71/0x73) → execution
(0x10/0x70/0x72). Log every negative path; a service with only positive-path tests is incomplete.
Every NRC in this table must be hit by at least one generated negative case per campaign.

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

## Rule 5 — Extract ingestion (AUTOSAR / XLS / ODX / YAML / JSON)

The generator accepts ONE canonical input: the UDS test-spec (see `tools/diag-uds-testgen/`
schema). Adapters convert each native extract into that spec; adapters never invent services:

1. **AUTOSAR DEXT / ECU-C ARXML (preferred for AUTOSAR ECUs).** Parse Dcm/Dem/Fim-relevant
   elements: service table, session/security references, DID/DTC/RID catalogues, memory windows.
   Record the DEXT/ARXML file name + version/hash in every generated file header. Reference:
   AUTOSAR DEXT requirements R24-11 Doc ID 681.
2. **ODX/PDX (preferred for tester parity).** Parse DIAG-LAYER-CONTAINER: DIAG-SERVICE,
   REQUEST/POS-RESPONSE/NEG-RESPONSE params, DOPs, DTC-DOPs, TABLEs. ODX source + version
   recorded; ODX stays the oracle for DID/DTC encoding.
3. **CDD (CANdela).** Treat as authoring input equivalent to ODX; export ODX/PDX first where
   possible, else map CDD service/DID/DTC tables 1:1 into the spec with the CDD file + version.
4. **XLS/XLSX (OEM supplier sheets).** One row per testable item: `sid, subfunction, did/dtc/rid,
   session, security_level, addressing, precondition, expected_positive, negative_nrcs`.
   The importer validates SIDs/subfunctions against Rule 1 and rejects unknown rows with file +
   row number — it never silently drops them.
5. **YAML/JSON (canonical hand-off).** Direct authoring or merged intermediate; validated
   against `schemas/uds-test-spec.schema.json`. This is the committed artefact when no
   DEXT/ODX exists.
6. **OTX/OSX tester scripts.** Consumed as *sequence oracles* for FBL and routine flows
   (expected step order + assertions), not as service definitions. OTX package + version recorded.
7. Every adapter emits `spec provenance`: `{source_type, source_file, source_version, sha256,
   generated_at, generator_version}`. Provenance travels into generated tests and evidence.

Minimal canonical spec shape (full schema in `schemas/uds-test-spec.schema.json`):

```yaml
provenance: {source_type: dext|odx|cdd|xlsx|yaml|json|otx, source_file: "...", source_version: "..."}
ecu: {name: "DoorECU", sessions: [default, extended, programming], security_levels: [1]}
services:
  - sid: 0x22
    name: ReadDataByIdentifier
    supported: true
    dids:
      - id: 0xF190
        sessions: [default, extended]
        security: null
        addressing: [physical, functional]
  - sid: 0x19
    name: ReadDTCInformation
    supported: true
    subfunctions: [0x01, 0x02, 0x0A]
```

## Rule 6 — Test and validation code generation (positive + negative)

For every service in the spec the generator emits BOTH classes; a one-sided service fails the gate:

1. **Positive cases (per subfunction/resource).** For each supported SID × supported subfunction
   (or DID/DTC/routine/memory/file selector): nominal request in an allowed session (unlocked
   where required) → assert positive-response SID, echoed selectors, and payload shape. FBL
   positives assert the full sequence (0x10 programming → 0x27 → 0x31 erase → 0x34 → 0x36[n]
   → 0x37 → 0x31 checksum → 0x11). Each case carries `trace: [requirement, sid, subfunction,
   did/dtc/rid, odx/dext element, evidence-id]`.
2. **Negative cases (fixed template per service).** Emit at minimum, per supported SID:
   wrong-length/format (0x13), unsupported-subfunction (0x12, one unlisted value), wrong-session
   (0x7E/0x7F — each gated service executed in a disallowed session), locked-access without
   unlock (0x33), unknown-DID/DTC/routine/window (0x31), conditions-not-correct (0x22, one
   interlock violated), sequence error (0x24 — e.g. 0x36 before 0x34, 0x37 without 0x36),
   busy/pending handling (0x21/0x78 where applicable), transfer faults (0x70/0x71/0x73 for
   0x34–0x38), key faults (0x35/0x36/0x37 for 0x27), plus unsupported-SID (0x11) once per campaign.
   For SPR-capable services emit SPR=1 (no positive response expected) and SPR=0 variants.
   Execute each negative case on physical addressing (assert exact NRC) AND functional
   addressing (assert silence).
3. **Session/security matrix.** Every gated SID × {default, extended, programming} ×
   {locked, unlocked} × {physical, functional}. Session-transition tests: S3 timeout → default;
   programming → reset → default; 0x28/0x85 state reverts on session change per project.
4. **Validation layer (stakeholder/needs, `skills/validation/`).** Above the generated service
   matrix, emit validation scenarios: workshop tester workflow, FBL reflash acceptance, DTC
   read/clear driving a warning-lamp/HMI state, OBD legislated availability in default session.
   Validation cases reference needs IDs, run with representative users/hardware, and record
   pre-registered acceptance thresholds — they are not derived from requirements alone.
5. **Output layout (per ECU variant).** `test/gen/<ecu>/uds_<sid>_<name>.py` (or CAPL/C per
   project), `test/gen/<ecu>/neg_<sid>_<name>.py`, `validation/gen/<ecu>/diag_acceptance.md`,
   `evidence/gen/<ecu>/uds_traceability.csv`, `evidence/gen/<ecu>/uds_provenance.json`.
   Generated files carry header `GENERATED BY <tool> <version> FROM <source> — DO NOT EDIT`;
   hand-written deltas live in `test/diag/` overlays, never in generated files.
6. **Determinism.** Same spec + same tool version → byte-identical output (sorted emission,
   no timestamps in bodies, provenance isolated in the JSON sidecar). Golden files committed;
   CI diffs generator output and fails on uncommitted drift.

## Rule 7 — Tool-creation contract (how to build/extend the generator)

1. **Manifest + schema first.** Every diag testgen tool ships `manifest.yaml` (per
   `schemas/tool.schema.json`: id, version, purpose, deterministic=true, evidence=true),
   an input schema (`schemas/uds-test-spec.schema.json`), and a versioned CLI:
   `generate_uds_tests --spec <spec.yaml|json> --out <dir> --ecu <name> [--format py|capl|c]`.
2. **Adapter separation.** `adapters/dext.py`, `adapters/odx.py`, `adapters/cdd.py`,
   `adapters/xlsx.py`, `adapters/otx.py` each do ONLY extract→spec translation with row/element
   error locations; `core/matrix.py` does ONLY spec→case expansion (Rules 1–2 × Rule 6);
   `core/emitters.py` does ONLY case→code rendering. No adapter invents SIDs; `core/matrix.py`
   rejects out-of-matrix SIDs with an error, never a warning.
3. **Stdlib-first, pinned deps.** Reference implementation (`tools/diag-uds-testgen/`) uses
   Python ≥3.11 stdlib only (yaml/json via PyYAML where available, openpyxl optional for XLSX);
   any extra dependency is pinned and recorded in provenance.
4. **Golden self-test.** `tools/diag-uds-testgen/tests/` holds a minimal spec + expected outputs;
   `pytest` compares generator output byte-for-byte. A generator change without updated goldens
   fails CI.
5. **Evidence output.** Every run writes `uds_provenance.json` (input hash, output hash,
   tool version, source id/version) consumable by `skills/evidence/` and `skills/test-automation/`
   farm logs.

## Integration and test strategy

- Service-matrix pack: every SID x session x locked/unlocked x functional/physical,
  asserting the exact NRC on failure (now GENERATED from the extract, Rules 5–6).
- Tester-in-the-loop: ODX-driven regression on simulated and real ECU; DoIP denial and S3 cases.
- FBL campaign: download → verify → boot trial image; power-loss at erase/transfer/exit each
  leaves a bootable image (with `skills/bootloader/` matrix).
- Security tests: wrong-key, attempt-exhaustion, lockout-timing, downgrade rejection;
  SecOC-failure injection where SecOC is on.
- Generator self-tests: golden spec → golden vectors green in CI; adapter fixtures per
  source type (DEXT sample, ODX sample, XLSX sample, YAML/JSON sample).

## Traceability

- Requirement → SID/DID/DTC/routine → `src/` handler → `test/gen/` case → ODX/DEXT element → evidence id.
- Standards cited as number + version + identifier only with landing URL.
- Provenance sidecar (`uds_provenance.json`) is a required trace input, not an accessory.

## Compliance mapping (via overlays, not duplication)

- ISO 26262:2018 (diagnostic faults as safety mechanisms where claimed);
  ISO/SAE 21434 (security-access, key management, TARA linkage); UNECE R155/R156 touchpoints.
- Emissions/OBD regulation applicability recorded project-side. Never claim type approval.
- AUTOSAR SRS Diagnostic / DEXT / ATS DiagnosticServices referenced by document ID + release only.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill automotive-diagnostics` → PASS.
2. Service-matrix pack green; every NRC in Rule 2 hit at least once (measured, not asserted).
3. Session-timeout, lockout-timing, FBL power-loss cases demonstrated.
4. ODX/DEXT source/version/hash recorded for all generated tester data (`uds_provenance.json`).
5. Test keys absent from production build; lockout counters in NVM proven.
6. Traceability complete incl. generated `uds_traceability.csv`; no copied normative text.
7. Generator determinism proven: two consecutive runs byte-identical; golden tests green.
8. Safety/security deltas flagged for human review before PR.

Load task-specific domain/platform/rule overlays before execution.
