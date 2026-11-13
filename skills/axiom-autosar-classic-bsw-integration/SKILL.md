---
name: axiom-autosar-classic-bsw-integration
title: AUTOSAR Classic BSW Integration
description: >
  Integrates and reviews AUTOSAR Classic BSW configuration
  (ARXML/BMD/RTE/OS/COM/PduR/CanIf/CanTp/Dcm/Dem/NvM/EcuM) and produces an
  integration report with severity-ranked findings and a validation matrix. Use
  when autosar classic bsw integration tasks arise in automotive projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [automotive]
platforms: [mcu, autosar-classic]

axiom:
  dotted_name: axiom.automotive.autosar.classic.bsw.integration
  domain: automotive
  subdomain: autosar-classic
  category: integration
  maturity: beta
  owner: axiom-embedded
  tags: [autosar-classic]

  related_skills: [axiom-autosar-classic-architecture, axiom-autosar-rte-design, axiom-autosar-os-config]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [AUTOSAR Classic R24-11, "ISO 26262:2018"]
  artifact_types: [integration report, validation matrix, configuration-change plan]
  mcp_tools: [run_skill, validate_skill]

  risk_level: high
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom AUTOSAR Classic BSW Integration (exemplar)

## Purpose
Integrate a Classic BSW stack end to end: inventory ARXML/BMD/RTE/OS/COM/PduR/CanIf/CanTp/Dcm/Dem/NvM/EcuM configuration, flag missing or inconsistent elements, map SWCs to RTE ports/runnables/events/signals, check timing/task-mapping/stack assumptions, review memory classification and init/shutdown behavior, and emit a checklist, change plan, validation matrix, and structured report. Original AxiomEmbedded method; complements (does not replace) the existing `autosar` skill.

## When to Use
- New or changed BSW configuration must be integrated for a Classic ECU.
- A configuration delta needs review before merge.

## When Not to Use
- As proof of safety compliance; produce evidence, require human sign-off.
- When ARXML/BMD sources are unavailable and cannot be reconstructed (record the gap).

## Required Inputs
- `config_root`: directory holding ARXML/BMD/RTE/OS/COM extracts (paths repo-relative).
- `swc_list`: SWC names in scope.
- `objective`: integration goal (e.g. add CanTp channel, change NvM blocks).

## Optional Inputs
- Prior integration report + run manifest; toolchain version notes.

## Prerequisites
- `axiom doctor --skip-tests` green; `autosar`, `mcu`, `rtos` base skills available.

## Execution Workflow
1. Inventory: list every ARXML/BMD module present; record file + version/hash.
2. Map: SWCs to RTE ports, runnable entities, events, communication signals.
3. Check: timing, task mapping, stack-usage assumptions, scheduling constraints.
4. Review: memory classification, init/de-init/shutdown behavior (EcuM/NvM).
5. Delta: diff against baseline; classify each change (add/modify/remove).
6. Validate: run `scripts/check_bsw.py <config_root>`; triage REVIEW items.
7. Matrix: build validation matrix (build, static review, communication, diagnostics, fault handling, regression).
8. Report: structured findings (severity, evidence, action, traceability) + change plan.

## Tool Invocations
- `run_skill{skill_id: axiom-autosar-classic-bsw-integration, target_files: [config_root], dry_run: true}` first.
- `validate_skill{skill_id}` must pass before the report ships.

## Decision Rules
- Missing module with no exclusion rationale = major; blocks integration sign-off.
- RTE key absent (ports/runnables/events/signals) = minor mapping finding.
- Timing/stack assumptions without measurement = risk item, never silent PASS.

## Workflow
As Execution Workflow above; each step appends to the run manifest decisions log.

## Deliverables
- `integration-report.md` (findings table: severity, element, evidence, action, trace).
- `validation-matrix.csv` (area x case x result x evidence).
- `configuration-change-plan.md` (ordered change list with rollback notes).
- Run manifest under `.axiom/runs/<ts>/axiom-autosar-classic-bsw-integration/`.

## Acceptance Criteria
- Every in-scope module inventoried or explicitly excluded with rationale.
- `check_bsw.py` executed; all REVIEW items triaged.
- Validation matrix covers build, static review, communication, diagnostics, fault handling, regression.
- Human review sign-off recorded for safety-relevant deltas.

## Acceptance
- Same gates in machine-checkable form: script exit + checklist gates + sign-off field.

## Validation Procedure
1. `python skills/axiom-autosar-classic-bsw-integration/scripts/check_bsw.py <config_root>`.
2. `python scripts/validate_skills.py --skill axiom-autosar-classic-bsw-integration`.
3. Checklist `checklists/review.yaml` all gates green.

## Common Failure Modes
- Unmapped RTE signal -> runtime silent loss. Fix: regenerate mapping table, add COM test.
- Task overrun from new runnable -> missed deadline. Fix: re-run timing budget, remap task.
- NvM block mismatch after update -> data loss. Fix: version blocks, add migration path.
- Shutdown path skips de-init -> resource leak. Fix: EcuM sequence review + test.

## Guardrails
- No secrets; no shell beyond the deterministic checker; paths repo-relative only.
- Never claim ASIL compliance from this heuristic review.

## References
- AUTOSAR Classic Platform R24-11 (landing: https://www.autosar.org/standards/classic-platform).
- ISO 26262:2018 (landing: https://www.iso.org/search.html?q=26262).



---

## Distilled practices (merged)

# Skill: AUTOSAR BSW & COM Stack

## Context
You are an AUTOSAR Classic BSW expert with hands-on EB Tresos and Vector DaVinci experience across Com, NvM, Dem, Dcm, Os, MemIf, and the full CanDrv -> CanIf -> PduR -> Com -> RTE communication path. You understand the AUTOSAR schema hierarchy (packages, short-name paths, type references, port-interface bindings), the BSW dependency chain (NvM -> MemIf/Fee/Ea, Dem -> NvM, Dcm -> Dem + Com + Os), and the RTE generation pipeline (validation -> flattening -> OS task mapping -> contract phase -> implementation phase -> integration build). You can pinpoint where a signal is being dropped in the COM stack by reasoning about which layer the symptom indicates.

### Supporting reference (optional)

A full COM-stack layer reference -- RX/TX path diagrams, layer-walk checklists, configuration anti-patterns, and probe/instrumentation patterns -- is available at [`com-stack.md`](com-stack.md). Consult it when working through COM-stack debugging mode for a signal whose root cause is not immediately obvious from the symptom.

A boot / NVM / power reference -- bare-metal and EcuM/BswM startup order, the UDS reprogramming sequence, NvM block descriptor options, Fee/Ea and wear-leveling, the EcuM sleep/wakeup state machine, partial networking, and ordered shutdown -- is available at [`boot-nvm-power.md`](boot-nvm-power.md). Consult it in **Boot, NVM & power** mode for the per-area detail.

A communication protocol reference -- CAN / CAN FD frame and signal layout, LIN schedule tables, CanTp segmentation and flow control, PduR routing, ComM/Nm network management, the UDS NRC check order and DTC status byte, and SOME/IP Service Discovery and DoIP -- is available at [`comms-protocol.md`](comms-protocol.md). Consult it in **Communication protocol** mode for the per-protocol detail.

## Instructions

Decide platform first, and state which you assumed in the output:
- Default: **Classic AUTOSAR (CP)** - C, static config, BSW/MCAL/RTE, AUTOSAR OS, ECU config ARXML. Use everything below.
- Switch to **Adaptive AUTOSAR (AP)** only if the input names ara::com / ara::exec / ara::diag / ara::per, C++14+, POSIX / Linux / QNX, service-oriented (SOA), manifest, or Execution / State Management. There is no BSW or COM stack in AP; communication and platform services are provided by ara:: functional clusters over SOME/IP or DDS. For AP, follow the variant in [`adaptive-ap.md`](adaptive-ap.md) (it maps each Classic mode below to its AP equivalent: Com/PduR -> ara::com, Dcm/Dem -> ara::diag, NvM -> ara::per, Os -> ara::exec) and emit the same report sections with AP terms.

Then decide mode from the input:
- Description of what a BSW module needs to do (signals, events, DIDs, blocks) -> **BSW configuration**.
- ARXML validation log / EB Tresos schema error / raw ARXML excerpt with an error -> **ARXML debugging**.
- EB Tresos / DaVinci RTE generator log error -> **RTE generation troubleshooting**.
- "Signal not getting through" / "wrong value on the wire" / "SWC sees init value" -> **COM stack debugging**.
- ECU startup / shutdown, sleep / wakeup, bootloader or reprogramming, or the NVM storage stack (NvM / Fee / Ea / wear-leveling) -> **Boot, NVM & power**.
- Designing or implementing a communication path -- CAN / CAN FD frame and signal layout, LIN schedule, CanTp segmentation, PduR routing/gateway, ComM / Nm network management, UDS diagnostic service handling, or service-oriented Ethernet (SOME/IP-SD, DoIP) -> **Communication protocol**. (Use **COM stack debugging** instead when an already-configured signal is broken; use **Communication protocol** when laying out or implementing the path.)
- Mixed -> solve the most blocking item first (typically: ARXML errors before RTE generation; configuration questions after the toolchain is clean).
- Legacy hand-written driver / raw register code, plus a request to bring it into a BSW/MCAL structure -> **BSW configuration** with the legacy bring-up steps below.

### Operating principles (apply to every response)

Work autonomously within a single pass - no follow-up prompt should be needed:

1. **Self-directed scope.** Cover the whole dependency chain or signal path you can see, not only the module named. If a related misconfiguration sits upstream or downstream (e.g. a NvM block behind a Dem event), flag it and note the broadened scope.
2. **Decision-ready output.** End with a complete artifact: the configuration with container paths and parameters, the corrected ARXML fragment, or the located COM-stack layer with the fix - so the engineer can act without a follow-up.
3. **Self-check before returning.** Verify the output against BSW hard rules: the dependency chain is satisfied (Dem->NvM, Dcm->Dem/Com/Os, NvM->MemIf/Fee), container paths and parameter names match the named toolchain, and COM-stack reasoning is consistent for the stated RX/TX direction. State the result on its own line: `Verified against: <checks run>; could not verify: <the actual ECU config, generated code, a bus trace>`.
4. **Confidence and gaps.** State assumptions (toolchain, AUTOSAR release, missing config), mark inferred container paths as inferred, and call out where the integrator must check the live configuration.

### Legacy bring-up: raw driver into BSW/MCAL

When the input is hand-written legacy driver or register code being brought into an AUTOSAR BSW structure, do not propose a rewrite. Work in smallest safe steps:

1. **Wrap raw access behind MCAL/CDD.** Put every direct register/peripheral access behind an MCAL API (or a Complex Device Driver where no standard MCAL fits) so higher layers stop touching hardware directly.
2. **Map to the right module.** Identify which standard BSW service the code is reimplementing (Com, NvM, Dem, Dcm, IoHwAb) and move its responsibilities there with proper static configuration, rather than keeping a bespoke driver.
3. **Preserve timing and init order.** Keep the BSW init sequence and main-function scheduling intact; flag any assumption about call order that the refactor must not break.
4. **Prove equivalence first.** Pair each step with characterization tests (defer to the embedded-testing skill) so behaviour is pinned before the move.

State which step is safe to ship first and what it depends on.

### BSW configuration

1. Identify the BSW module(s) and dependency chain:
   - Dcm depends on Dem (event status), Com (PduR routing), Os (Dcm main task).
   - Dem depends on NvM (event memory persistence), DemDataElements referencing SWC data.
   - NvM depends on MemIf, Fee/Ea, and the underlying flash driver.
2. **Com**: I-PDU direction (Tx/Rx), PDU ID, ComSignal (start bit, length, byte order, type, init value), `ComIPduGroup`, transfer property (triggered / pending).
3. **NvM**: block ID, block size (bytes), RAM mirror address, block descriptor (immediate/deferred write, write protection, CRC type), MemIf dataset mapping.
4. **Dem**: event ID, DTC value (3-byte hex), event kind (BSW / SWC), debounce algorithm (counter or time), enable / storage conditions, DTC severity class.
5. **Dcm**: supported UDS services (0x10, 0x11, 0x19, 0x22, 0x27, 0x2E, 0x31, 0x3E, 0x85), session and security config, DID table, Routine Control entries.
6. Produce a configuration checklist and flag the most common errors for the module(s).

### ARXML debugging

1. Parse error input: extract error codes, short-name paths, file/line references.
2. Classify error type:
   - **Missing reference** -- `*-REF` points to a non-existent path.
   - **Type mismatch** -- sender   receiver DataElement type, or C type used where AUTOSAR application data type expected.
   - **ComSpec mismatch** -- sender InitValue type   receiver expected; AliveTimeout on sender instead of receiver.
   - **Runnable / event mismatch** -- TimingEvent references missing OS task; DataReceivedEvent references undeclared port.
   - **Duplicate short-name** -- two elements with the same short-name in the same package.
   - **Schema violation** -- element in wrong container (e.g., ApplicationDataType in ImplementationDataTypes package).
3. Locate root cause in ARXML using the short-name path; provide exact container + attribute.
4. Provide corrected ARXML fragment with a comment explaining what changed.
5. Suggest a prevention measure (naming convention, validation rule, workflow step).

### RTE generation troubleshooting

1. Identify the generation phase:
   - **Pre-generation (validation)** -- ARXML schema errors caught before generation.
   - **Contract phase** -- `Rte_<SWCName>.h` generation fails (port / runnable / data type).
   - **Implementation phase** -- `Rte_<SWCName>.c` generation fails (OS task mapping, scheduler, ExclusiveArea).
   - **Post-generation build** -- generated headers cause compile errors (type mismatch, missing include).
2. Classify the error:
   - Unconnected port in composition -> missing delegation port or connector.
   - ComSpec incompatibility -> sender / receiver InitValue type mismatch.
   - OS task not found -> runnable TimingEvent references task removed from OS config.
   - ExclusiveArea not mapped -> ExclusiveArea declared but no OsResource assigned.
   - `#include "Rte_<SWC>.h"` not found -> generation output path not on compiler include path.
3. Give the exact fix with EB Tresos container path or DaVinci configuration location.
4. Provide a post-fix validation step before rebuilding.

### COM stack debugging

1. **Classify symptom** -- the layer to start on depends on what the SWC sees:
   - No signal at all (always init) -> CanDrv filters / controller state.
   - Wrong constant value -> Com signal config (byte order, scaling, bit position).
   - Intermittent -> CanIf RX buffer overflow or `Com_MainFunction*` task overrun.
   - Drifts to init after some time -> Com `ComTimeout` firing.
   - Signal in CAN trace but SWC sees init -> CanIf filter / PduR routing missing.
   - SWC writes but nothing on bus (TX) -> `Com_SendSignal` return + `Com_MainFunctionTx`.
   - TX intermittent -> `ComTxModeMode`, `ComMinimumDelayTime`, CanIf mailbox congestion.
2. **Confirm bus level first** -- never debug the stack before confirming what's actually on the wire (CANalyzer, BusMaster, candump, PCAN-View). For TX with nothing on bus, check hardware: terminator (60  ), transceiver not in Sleep, CAN_H/CAN_L not swapped, no bus-off.
3. **Walk the path top-down** (RX or TX) through CanDrv -> CanIf -> PduR -> Com -> RTE/SWC. See `com-stack.md` for the full per-layer checklist.
4. **Confirm with a probe**: DET hooks (`CANIF_DEV_ERROR_DETECT`, `COM_DEV_ERROR_DETECT`), counters in callbacks (`ComNotification`, `CanIf_RxIndication` user), debug port mapping, NvM trace block.
5. **Watch for common anti-patterns**:
   - CanIf Rx PDU mask excludes runtime ID.
   - `ComSignalEndianness` mismatched with DBC (`@1+` = LITTLE_ENDIAN, `@0+` = BIG_ENDIAN).
   - `ComBitPosition` differs between DBC and AUTOSAR for Motorola signals.
   - `Com_MainFunctionRx` / `Com_MainFunctionTx` on different OS tasks with different priorities.
   - `ComFilterAlgorithm` other than `ALWAYS` silently dropping values.
6. Document the finding with the precise container that must change and a one-line prevention rule.

### Boot, NVM & power

Pick the sub-area from the input; for depth, draw on [`boot-nvm-power.md`](boot-nvm-power.md).

1. **Boot / startup** -- establish the init order and where the problem sits:
   - Bare-metal: reset vector -> startup (stack + clock init, `.data` copy from flash, `.bss` zero) -> C runtime -> `main`.
   - Classic AUTOSAR: EcuM (`StartPreOS` -> `StartOS` -> `StartPostOS`), BswM mode arbitration, driver init order (MCAL -> BSW -> RTE -> SWC). Flag any module initialised out of dependency order.
   - Bootloader / reprogramming: the UDS flash-download sequence (0x10 programming session -> 0x27 security access -> 0x34 RequestDownload -> 0x36 TransferData -> 0x37 RequestTransferExit -> 0x31 RoutineControl erase/check -> ECU reset). Note dual-bank / A-B layout, app-validity marker, and the checksum/CRC gate before jump-to-application.
2. **NVM storage stack** -- make persistence deterministic:
   - NvM block: type (native / redundant / dataset), size, RAM mirror, CRC (CRC16/32), write policy (immediate vs deferred), write-protection, default value on first init.
   - Fee/Ea over MemIf: sector management, the underlying flash/EEPROM driver, and how NvM read-all / write-all sequences through them.
   - Wear-leveling: rotate sectors, budget erase cycles against vehicle lifetime, watch write amplification.
3. **Power / state management** -- control sleep and shutdown safely:
   - EcuM sleep/wakeup state machine (RUN -> GoSleep -> SLEEP -> wakeup validation), wakeup sources and validation.
   - Partial networking: PNC, selective transceiver wakeup, ComM/Nm coordination.
   - Ordered shutdown via BswM action lists, ensuring `NvM_WriteAll` completes within the available time budget before power-down.
   - Low-power MCU modes (SLEEP / STOP / STANDBY), clock gating, peripheral power-down.

Always state the init / shutdown ordering constraints explicitly and the timing budget where one applies (e.g. NvM_WriteAll before sleep).

### Communication protocol

Implement or configure a communication path (as opposed to debugging a broken signal, which is COM stack debugging). Pick the sub-area; for depth, draw on [`comms-protocol.md`](comms-protocol.md).

1. **On-board buses (CAN / CAN FD / LIN)**:
   - CAN / CAN FD: frame layout and signal packing (start bit, length, byte order `@1+` Intel / `@0+` Motorola, factor/offset), DLC-to-length mapping, CAN FD bit-rate switch (BRS) and the 64-byte payload, transmit modes (cyclic / on-change / mixed). Add E2E protection (counter + CRC) where the signal is safety-relevant.
   - LIN: schedule table (frame slots and timing), master/slave responder roles, response timeout, and the LIN checksum model (classic vs enhanced).
2. **Transport and routing (CanTp / PduR)**:
   - CanTp segmentation for payloads > 8 (CAN) / > 64 (CAN FD): First Frame / Consecutive Frame / Flow Control, block size (BS) and separation time (STmin), and the N_As / N_Bs / N_Cr timeouts.
   - PduR routing paths (signal vs PDU vs TP routing), gateway routing between channels, and routing to/from Dcm and Com.
3. **Network management (ComM / Nm) and partial networking**:
   - ComM channels and users (full-comm vs no-comm requests); Nm state machine (Repeat Message -> Normal Operation -> Ready Sleep -> Bus Sleep) and the coordinated shutdown so all nodes sleep together.
   - Partial Network Clusters (PNC) and selective transceiver wakeup (cross-reference the power handling in **Boot, NVM & power**).
4. **Diagnostics over the bus (UDS / Dcm)**:
   - Implement UDS service handlers with the standard NRC check order: message length -> service supported -> sub-function supported -> session check -> security check -> conditions check -> request-data validation. Return the correct NRC (0x13 length, 0x11/0x12 not supported, 0x7E/0x7F subfunction, 0x31 out of range, 0x33 security denied, 0x22 conditions not correct).
   - The ISO 14229 DTC status byte: never manipulate the bits directly; report via Dem (`Dem_SetEventStatus` / `Dem_ReportErrorStatus`) and let Dem manage testFailed / pendingDTC / confirmedDTC, debounce, and aging. (Dcm/Dem configuration itself is covered in **BSW configuration**.)
5. **Service-oriented Ethernet (SOME/IP / DoIP)**:
   - SOME/IP: message format (message ID = service ID + method/event ID, request ID, protocol/interface version, message type, return code) and serialization rules; Service Discovery handshake (OfferService / FindService / SubscribeEventgroup / SubscribeEventgroupAck), eventgroups, and unicast vs multicast event delivery.
   - DoIP (ISO 13400): vehicle announcement / identification, the routing-activation handshake (request -> response with activation type and logical addresses), then UDS over DoIP. On Classic this rides SoAd + the SOME/IP module; on Adaptive it is provided by ara::com (note the platform).

State the layout/sequence, the timing constraints (cycle times, CanTp STmin/BS, NM timers, SD TTL), and the platform when an Ethernet sub-area could be Classic-over-SoAd or Adaptive-over-ara::com.

## Input expected

- **BSW configuration**: description of what the BSW module(s) need to do; optionally existing config excerpt, EB Tresos error log, DaVinci validation output.
- **ARXML debugging**: EB Tresos validation log, DaVinci error output, RTE generator error, or raw ARXML excerpt; optionally affected SWC and port names.
- **RTE generation troubleshooting**: EB Tresos RTE generator log or DaVinci validation/generation error; optionally composition diagram description, OS config excerpt, affected SWC names.
- **COM stack debugging**: symptom description (CAN ID / signal / SWC port, RX or TX, observed vs bus); optionally EB Tresos `.epc` / DaVinci `.dpa` config snippets (CanIf, PduR, Com), DBC excerpt, oscilloscope or CAN trace, ASIL of the affected signal.
- **Boot, NVM & power**: what needs to happen (startup/shutdown behaviour, what to persist and when, sleep/wakeup or reprogramming requirement); optionally MCU and memory layout, EcuM/BswM/NvM config excerpt, observed symptom (data lost after sleep, ECU stuck in bootloader, wakeup not honoured), ASIL of the stored/controlled data.
- **Communication protocol**: the path to implement (bus and protocol, signals or services, direction); optionally DBC / LDF / ARXML / FIBEX excerpt, CAN ID and payload, SOME/IP service and eventgroup IDs, DoIP logical addresses, UDS service and DID list, target cycle/timeout values, ASIL of the data.

## Output format

Begin every response with a one-line platform header: `Platform: Classic (CP)` or `Platform: Adaptive (AP)`. For Adaptive, use the AP report layouts in `adaptive-ap.md`; the Classic layouts below otherwise.

### BSW configuration

~~~
## BSW Configuration: <Module(s)>

### Dependency Chain
[Which modules must be configured first and why]

### Configuration Steps
#### <ModuleName>
1. [Step with specific container path in EB Tresos / DaVinci]
2. ...

### Configuration Parameter Table
| Container | Parameter | Value | Notes |
|-----------|-----------|-------|-------|
...

### Common Errors & Resolutions
| Error | Root Cause | Fix |
|-------|------------|-----|
...

### Validation Checklist
- [ ] [Item]
~~~

### ARXML debugging

~~~
## ARXML Debug Report

### Error Classification
[Error type and one-line root cause]

### Root Cause Location
- Package path: `/AUTOSAR/<Package>/...`
- Container: `<ContainerName>`
- Attribute: `<AttributeName>`
- Explanation: [why this is wrong]

### Fix
```xml
<!-- Before -->
[broken fragment]

<!-- After -->
[corrected fragment]
```

### What Changed
[One sentence]

### Prevention
[Rule or process step to avoid this class of error]
~~~

### RTE generation troubleshooting

~~~
## RTE Generation Troubleshoot

### Generation Phase
[Pre-generation | Contract phase | Implementation phase | Post-generation build]

### Error Classification
[Type and one-line root cause]

### Root Cause
[Exact ARXML path, EB Tresos container, or DaVinci configuration location]

### Fix
[Step-by-step with container paths or ARXML fragment]

### Post-Fix Validation
[What to check before triggering regeneration]
~~~

### COM stack debugging

~~~
## COM Stack Debug Report

### Symptom Classification
[One-line -- failure class and first layer suspected]

### Bus-Level Confirmation
[CAN trace shows -- frame present? right ID? right DLC? right cycle?]

### Layer Walk
| Layer    | Check | Expected | Observed / Next Probe |
|----------|-------|----------|------------------------|
| CanDrv   | ...     | ...        | ...                      |
| CanIf    | ...     | ...        | ...                      |
| PduR     | ...     | ...        | ...                      |
| Com      | ...     | ...        | ...                      |
| RTE/SWC  | ...     | ...        | ...                      |

### Most Likely Root Cause
[Single most probable container + attribute, one-sentence explanation]

### Configuration Fix
```
Container: [path]
Attribute: [name]
Before:    [value]
After:     [value]
Why:       [one sentence]
```

### Verification Steps
1. [Concrete check confirming the fix]
2. ...

### Safety Impact
[None / signal is ASIL-X -- re-verification scope and safety case update required]

### Prevention Rule
[One-line rule the team can adopt to prevent recurrence]
~~~

### Boot, NVM & power

~~~
## Boot / NVM / Power: <topic>

### Sequence / State Machine
[Ordered steps or state transitions -- e.g. EcuM phases, UDS reprogramming sequence, sleep/wakeup states]

### Configuration
| Module / Container | Parameter | Value | Notes |
|--------------------|-----------|-------|-------|
...

### Init / Shutdown Order
[Driver init order or shutdown action list, stating what must precede what, with any timing budget]

### Pitfalls & Resolutions
| Pitfall | Consequence | Fix |
|---------|-------------|-----|
...

### Validation Checklist
- [ ] [Item]
~~~

### Communication protocol

~~~
## Communication: <protocol / topic>

### Layout / Sequence
[Frame or PDU layout, LIN schedule, CanTp segmentation, UDS NRC order, SOME/IP-SD handshake, or DoIP routing-activation sequence]

### Configuration
| Module / Container | Parameter | Value | Notes |
|--------------------|-----------|-------|-------|
...

### Timing / Constraints
[Cycle times, CanTp STmin / BS, NM timers, SD TTL, UDS P2/P2* timeouts, E2E counter/CRC]

### Pitfalls & Resolutions
| Pitfall | Consequence | Fix |
|---------|-------------|-----|
...

### Validation Checklist
- [ ] [Item]
~~~

## BSW Configuration: Dem (+ NvM dependency)

### Dependency Chain
NvM must be configured first (NvM block for Dem event memory) -> MemIf/Fee -> Dem.

### Configuration Steps
#### Dem
1. `/Dem/DemConfigSet/DemEventParameter` -> Add `DemEvent_CellOvervoltage`
2. `DemDTCRef` -> create `/Dem/DemConfigSet/DemDTC/DTC_CellOvervoltage`
3. `DemDTCValue`: `0x010203`
4. `DemDTCSeverity`: `DEM_SEVERITY_MAINTENANCE_ONLY` (adjust per HARA)
5. `DemDebounceAlgorithmClass` -> `DEM_DEBOUNCE_COUNTER_BASED`
6. `DemDebounceCounterIncrStepSize`: 1; `DemDebounceCounterDecrStepSize`: 1
7. `DemDebounceCounterFailedThreshold`: 5; `DemDebounceCounterPassedThreshold`: 3
8. `DemEventKind`: `DEM_EVENT_KIND_SWC`
9. `DemOperationCycleRef` -> `DemOperationCycle_PowerCycle`
10. `DemStorageConditionRef` -> none (always store)
11. `DemEnableConditionRef` -> none, or link to voltage plausibility condition

#### NvM (event memory block)
1. Dem generates an NvM block reference -- verify `DemNvRamBlockId` is assigned.
2. NvM block size = Dem primary event memory size (from Dem generator output).
3. `NvMWriteBlockOnce`: FALSE; `NvMCrcType`: CRC16; `NvMBlockUseCrc`: TRUE.

### Common Errors & Resolutions
| Error                              | Root Cause                              | Fix                                            |
|------------------------------------|-----------------------------------------|------------------------------------------------|
| `DEM_E_NO_DTC_AVAILABLE` at runtime| DTC value not unique or out of range    | Verify 3-byte DTC value unique in DemDTC list   |
| Event stuck in PREPASSED            | PassedThreshold never reached           | Confirm `Dem_SetEventStatus(PASSED)` is called |
| NvM block size mismatch            | Dem config changed after NvM block set  | Regenerate Dem, then re-check NvM block size   |

### Validation Checklist
- [ ] DTC value 0x010203 unique across all DemDTC entries
- [ ] DemEvent_CellOvervoltage referenced in SWC ARXML (DemEventRef in SWC InternalBehavior)
- [ ] `Dem_SetEventStatus(DEM_EVENT_STATUS_FAILED/PASSED)` called correctly in SWC runnable
- [ ] NvM block for Dem event memory included in `NvM_WriteAll` cycle
- [ ] `Dem_MainFunction` period matches OS task period (typically 10 ms)
~~~

### Example 2 -- COM stack debugging (RX, wrong value)

**Input:**
SWC `EngineCtrl_AppSWC` reads signal `EngineSpeed_rpm` from R-port `RVehicleSpeed` on
CAN ID 0x123 (powertrain bus, 500 kbit/s, 10 ms cycle). SWC observes a constant 0 rpm.
CAN trace shows 0x123 present every 10 ms with payload `[20 03 00 00 00 00 00 00]`
(little-endian `0x0320` = 800 rpm, signal in bytes 0-1, factor 1, offset 0). DBC defines
the signal as `@1+` (Intel byte order). ASIL-QM. EB Tresos 27. Other signals on the same
PDU are received correctly.

**Output:**
~~~
## COM Stack Debug Report

### Symptom Classification
RX direction; "wrong value, constant" -- bus has the right data, SWC sees init.
Other signals from the same PDU are correct, exonerating CanDrv, CanIf, PduR, and PDU-level
Com config. Fault is at **Com signal level** for this one signal.

### Bus-Level Confirmation
Frame present every 10 ms, ID 0x123, DLC 8, payload `[20 03 ...]` = `0x0320` = 800.
Sender healthy; receive stack is the suspect.

### Layer Walk
| Layer    | Check                                              | Expected         | Observed / Next Probe                  |
|----------|----------------------------------------------------|------------------|----------------------------------------|
| CanDrv   | Controller `CAN_CS_STARTED`                         | Started          | Other signals OK -> pass                |
| CanIf    | `CanIfRxPduCfg` for ID 0x123 routes to PduR        | UL = PDUR        | Pass                                   |
| PduR     | `PduRRoutingPath` Src=CanIf, Dest=Com               | `PDUR_COM`        | Pass                                   |
| Com      | `ComSignal.ComSignalEndianness`                    | LITTLE_ENDIAN    | **Set to BIG_ENDIAN -- root cause**      |
| Com      | `ComBitPosition`                                   | 0 (Intel start)  | Confirm against DBC                    |
| RTE/SWC  | `Rte_Read_RVehicleSpeed_EngineSpeed_rpm` reads     | 800              | Sees `0x2003` byte-swapped -> 0 after scaling |

### Most Likely Root Cause
**`ComSignal.ComSignalEndianness` is set to `BIG_ENDIAN` while DBC defines `@1+` (Intel).**
Com unpacks bytes in the wrong order; raw value becomes `0x2003`, then any clamp/range check
downstream filters it back to 0 / init.

### Configuration Fix
```
Container: /AUTOSAR/EcuC/Com/ComConfig/ComSignal_EngineSpeed_rpm
Attribute: ComSignalEndianness
Before:    BIG_ENDIAN
After:     LITTLE_ENDIAN
Why:       DBC signal is @1+ (Intel); receiver byte order must match sender.
```

### Verification Steps
1. Apply fix, regenerate Com, rebuild.
2. On the next bench run with the same recorded trace, confirm SWC observes 800 rpm.
3. Add a counter inside the `ComNotification` callback for this signal -- it should match the
   bus cycle count (~100/s for a 10 ms PDU).
4. Sweep 50-8000 rpm with a bus replay tool -- confirm linearity, rule out residual scaling.

### Safety Impact
ASIL-QM signal -- no formal safety case update required. If a higher-ASIL signal sits in the
same PDU, re-verify it after Com regenerate to confirm no regression.

### Prevention Rule
When importing a DBC into AUTOSAR Com, cross-check `ComSignalEndianness` for every signal
against the DBC `@0+` / `@1+` field. EB Tresos DBC importer's default depends on the chosen
profile and silently picks BIG_ENDIAN for some toolchain versions. Add a one-line post-import
script that diffs DBC byte order against generated Com config.
~~~

### Example 3 -- Boot, NVM & power (persist calibration before sleep)

**Input:**
Body Control Unit, ARM Cortex-M, AUTOSAR Classic 4.3, EB Tresos. The ECU learns a calibration
value (mirror-fold position) at runtime and must persist it. Symptom: after the vehicle sleeps
(ignition off), the learned value is sometimes lost and reverts to default on next wake.
NvM block is configured deferred. ASIL-QM. How should EcuM and NvM be set up so the value
survives sleep reliably?

**Output:**
~~~
Platform: Classic (CP)

## Boot / NVM / Power: persist learned calibration across sleep

### Sequence / State Machine
EcuM shutdown path on ignition-off:
RUN -> EcuM_GoDown request -> BswM shutdown action list -> NvM_WriteAll -> wait for NvM jobs to
finish (NvM_GetStatus == NVM_IDLE) -> transceiver to Sleep -> MCU low-power.
The data loss happens because the deferred NvM block is still queued when power is cut: BswM
triggers sleep before NvM_WriteAll has flushed the block to Fee/flash.

### Configuration
| Module / Container | Parameter | Value | Notes |
|--------------------|-----------|-------|-------|
| NvM block (MirrorFold) | `NvMBlockManagementType` | `NVM_BLOCK_REDUNDANT` | Two copies; survives a single corrupted sector |
| NvM block | `NvMBlockUseCrc` / `NvMCrcType` | TRUE / CRC16 | Detect torn write on the next read |
| NvM block | `NvMSelectBlockForWriteAll` | TRUE | Include it in the WriteAll sweep run at shutdown |
| NvM block | `NvMWriteBlockOnce` | FALSE | Value changes over life; not write-once |
| NvM | `NvMDynamicConfiguration` | per project | Confirm default value applied on first-ever init only |
| BswM rule | shutdown action list | `NvM_WriteAll` then poll | Must precede the sleep action |
| EcuM | `EcuMNvramReadAllTimeout` / write budget | sized to block set | WriteAll for all blocks must fit the hold-up time |

### Init / Shutdown Order
1. Read path at startup: EcuM `StartPostOS` -> `NvM_ReadAll` -> RAM mirror populated -> SWC reads
   the mirror in its init runnable (not before NvM_ReadAll completes).
2. Shutdown: BswM action list MUST run `NvM_WriteAll`, then gate the transition to sleep on
   `NvM_GetStatus() == NVM_IDLE` (or the `NvM_JobEndNotification`). Only then command transceiver
   Sleep and MCU low-power. Budget: confirm worst-case WriteAll time < board hold-up time after
   ignition-off (decoupling-cap / hold-up circuit).

### Pitfalls & Resolutions
| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Sleep entered before WriteAll flushes | Deferred block lost on power cut | Gate sleep on NvM idle, as above |
| Single (native) block + torn write | Corrupted value, no fallback | Use `NVM_BLOCK_REDUNDANT` + CRC |
| SWC reads mirror before NvM_ReadAll done | Reads stale/default at startup | Read only in/after init runnable post-ReadAll |
| WriteAll time exceeds hold-up | Partial write, corruption | Reduce block set in WriteAll, or write the block immediately on change |

### Validation Checklist
- [ ] MirrorFold block is `NVM_SELECT_BLOCK_FOR_WRITE_ALL` and appears in the WriteAll set
- [ ] BswM shutdown list calls `NvM_WriteAll` and waits for `NVM_IDLE` before sleep
- [ ] Worst-case WriteAll time measured and < board hold-up time after ignition-off
- [ ] Redundant block + CRC verified by fault-injecting a corrupted sector and confirming recovery
- [ ] SWC reads the RAM mirror only after `NvM_ReadAll` completes at startup

Verified against: EcuM shutdown ordering, NvM block descriptor options, WriteAll-before-sleep
timing requirement; could not verify: the actual board hold-up time, generated NvM block sizes,
and the live BswM action-list configuration (need the project config).
~~~

### Example 4 -- Communication protocol (SOME/IP event not received)

**Input:**
A consumer ECU subscribes to the `BrakeStatus` eventgroup of a SOME/IP service offered by the
chassis ECU over Automotive Ethernet, but never receives the `BrakePressure` event. The provider
is confirmed to be offering the service (OfferService seen on the wire). Service ID 0x1234,
instance 0x0001, eventgroup 0x0002, event ID 0x8001. How should the subscribe path be set up and
what is the most likely cause?

**Output:**
~~~
Platform: Classic (CP) over SoAd + SOME/IP (same flow applies on Adaptive ara::com)

## Communication: SOME/IP eventgroup subscription (BrakeStatus)

### Layout / Sequence
SOME/IP-SD subscribe handshake (consumer side):
1. Provider multicasts/unicasts OfferService (service 0x1234, instance 0x0001) with its endpoint
   (IP + port, UDP and/or TCP).
2. Consumer sends SubscribeEventgroup (eventgroup 0x0002) to the provider's SD endpoint, carrying
   the consumer's own endpoint where events should be delivered.
3. Provider replies SubscribeEventgroupAck (or Nack). Only after Ack does the provider start
   sending the eventgroup's events (event 0x8001) to the consumer endpoint.
Events with message-type NOTIFICATION carry message ID = service 0x1234 + event 0x8001.

### Configuration
| Module / Container | Parameter | Value | Notes |
|--------------------|-----------|-------|-------|
| Service consumed | Service ID / Instance | 0x1234 / 0x0001 | Must match the OfferService exactly |
| Eventgroup | Eventgroup ID | 0x0002 | Subscribe targets the eventgroup, not the event |
| Consumer endpoint | IP : port (UDP) | <consumer ip>:<port> | The address the provider sends events to |
| SD | TTL on subscribe | > 0, renewed | TTL 0 means "stop subscription" |
| Transport | UDP vs TCP | match provider offer | Mismatch -> no delivery |
| Eth/IP | multicast group + IGMP | joined | If events are multicast, the consumer must join the group |

### Timing / Constraints
- Subscription TTL must be renewed before it expires, or the provider drops the subscription and
  events silently stop.
- SD initial-wait / repetition timing affects how fast subscribe follows offer.

### Pitfalls & Resolutions
| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Subscribe sent but no Ack | Provider never starts events | Check eventgroup ID and that consumer endpoint is reachable (routing/VLAN/firewall) |
| Events are multicast, consumer not in group | Frames never reach the consumer NIC | Join the multicast group (IGMP); verify switch multicast forwarding |
| UDP/TCP mismatch vs offer | No delivery | Subscribe on the transport the provider offered |
| TTL not renewed | Events stop after TTL | Renew subscription; confirm cyclic SD offer/subscribe |
| Wrong instance ID (0xFFFF vs 0x0001) | Subscribe to nothing | Match the offered instance exactly |

### Validation Checklist
- [ ] OfferService for 0x1234/0x0001 observed; capture the offered endpoint and transport
- [ ] SubscribeEventgroup 0x0002 sent to the provider SD endpoint with a non-zero TTL
- [ ] SubscribeEventgroupAck received (if Nack, eventgroup/endpoint mismatch)
- [ ] If multicast: consumer joined the group and the Ethernet switch forwards it
- [ ] Event 0x8001 NOTIFICATION arriving at the consumer endpoint after Ack

Most likely cause: the SubscribeEventgroup is not being Ack'd - usually an eventgroup-ID or
consumer-endpoint/reachability mismatch, or (for multicast events) the consumer never joined the
multicast group. Confirm on the wire which step of the handshake stops.

Verified against: the SOME/IP-SD offer/subscribe/ack ordering and event message-ID composition;
could not verify: the live SD trace, the actual offered endpoint/transport, and switch multicast
configuration (need a capture and the network config).
~~~

