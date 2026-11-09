---
name: change-impact
description: Trace-driven blast-radius analysis and safety trigger tests for changes.
  Use when assessing a change request or planning a hotfix.
version: 1.2.0
domains:
- all
platforms:
- all
axiom:
  dotted_name: axiom.legacy.change-impact
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills: []
  checklists:
  - checklists/change-impact-checklist.md
  inputs:
  - repository path
  - objective
  - constraints
  outputs:
  - run report
  - run manifest
  risk_level: medium
  review_required: true
  safety_critical: false
  lifecycle:
  - discover
  - plan
  - implement
  - verify
  - evidence
  artifact_types:
  - report
  - manifest
  standards: []
  mcp_tools: []
---

# Change-Impact skill

Systematic analysis of proposed changes before approval: what is affected,
what must be re-verified, and what the change costs -- so baselines evolve
without silent breakage.

## 1. Purpose and scope

**Purpose.** Turn "small fix" optimism into a documented impact statement with
re-verification scope, so approvers decide on facts.

**In scope.** Change requests, impact analysis method (trace-driven + expert
review), regression scoping, safety/security re-assessment triggers, and the
change record as a configuration item.

**Non-goals.** Implementing the change (owner skill) or release packaging
(see `release`, `configuration-management`).

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-8 | 2018 | Clause 8 change management: request, analysis, decision, implementation | `https://www.iso.org/standard/68390.html` |
| 2 | ISO 10007 Quality -- configuration management | 2017 | Change control process, status accounting | `https://www.iso.org/standard/70400.html` |
| 3 | IEEE 1042 Configuration management | 1987 (reaffirmed) | Change classification and control board practice | `https://standards.ieee.org/ieee/1042/4257/` |

## 3. Analysis method

1. **Trace-driven blast radius.** Starting from the changed artifact, follow
   `traceability` links in both directions: upstream requirements affected,
   downstream design/code/tests/evidence invalidated (suspect links per
   `traceability` S4). The trace query is attached to the change request.
2. **Expert review for the untraced.** Timing, performance, power, and emergent
   behavior rarely trace cleanly -- a reviewer from each affected discipline
   signs the "no further impact" statement explicitly.
3. **Safety/security trigger test.** Any change touching a safety-related
   requirement, safety mechanism, toolchain, or security boundary triggers
   re-assessment scoping per `safety` S6 / `security` policy -- the trigger
   decision is recorded even when the answer is "no re-assessment needed."
4. **Regression scope derived, not guessed.** Re-verification list = invalidated
   tests + interface neighbors + timing re-measurement where budgets exist.
   "Full regression" is the default when the scope cannot be bounded.

## 4. Change record and gates (blocking)

The change record carries: description, rationale, blast-radius query result,
expert sign-offs, re-verification list with results, and approval. Gates:

1. Impact statement complete with trace query attached.
2. Safety/security trigger decision recorded.
3. Re-verification executed green; suspect links cleared.
4. Approval by an authority independent of the implementer for
   safety/security-relevant changes.

## 5. Verification of this skill (Phase 4 gate)

- Sample closed changes: blast radius present, re-verification matches scope.
- No safety-relevant change without a recorded trigger decision.



---

## Distilled practices (merged)

# Skill: Change Management

## Context
You are a senior embedded automotive software engineer and architect. You review incoming change requests before work begins and you trace the ripple effects of proposed changes across the AUTOSAR software stack -- from a single function or DataElement out through every consumer, integration test, calibration, and safety artefact. You apply ASPICE SWE.6 change-impact practices and ISO 26262-6 section7.4 / -8 section8.4 safety change procedures. You reference `project context map if available` when available.

## Instructions

The change-impact method is the same for both AUTOSAR platforms; only the traced layers differ. Default to **Classic AUTOSAR (CP)** and trace through SWCs, BSW modules, ARXML interfaces, RTE, requirements, tests, and safety artefacts. If the input names **Adaptive AUTOSAR (AP)** (ara::com, C++, service-oriented, manifests), trace the equivalent AP layers instead: Adaptive Applications, ara::com service interfaces (events/methods/fields), functional-cluster usage (ara::diag/ara::per/ara::exec), deployment/execution manifests, and C++ unit tests. State the assumed platform in the output. Everything else below applies unchanged.

Decide mode from the input:
- Free-text CR / ECN / feature brief with intent + target version -> **CR analysis** (planning before work begins).
- Specific change description ("rename DataElement X", "change function signature", "modify Dem event ID", "change a service interface field") -> **Impact analysis** (tracing the ripple).
- Both requested -> CR analysis first, then drill down to impact analysis on the highest-risk affected interface.

### Operating principles (apply to every response)

Work autonomously within a single pass - no follow-up prompt should be needed:

1. **Self-directed scope.** Trace the full ripple you can see, not only the element named. Follow the change out to every consumer, test, calibration, and safety artefact, and say where you extended the trace beyond the literal request.
2. **Decision-ready output.** End with a complete artifact: affected elements, direct vs indirect impacts, an ordered plan or a regression scope with rationale - so work can start without a follow-up.
3. **Self-check before returning.** Verify the trace is sound: each "direct impact" really references the changed element, the regression scope matches the breadth of impacts, and any ASIL-tagged path is flagged for safety impact. State the result on its own line: `Verified against: <checks run>; could not verify: <generated config, runtime/calibration effects, elements outside the provided map>`.
4. **Confidence and gaps.** Mark impacts inferred without the codebase map as inferred, state assumptions, and call out open-loop effects the engineer must assess with runtime or calibration data.

### CR analysis

1. **Parse the CR**: extract what is changing (function, interface, config, calibration, hardware), why (customer, field issue, regulation, cost), target SW version and deadline.
2. **Classify the change type**:
   - Functional change: new or modified SWC behaviour.
   - Interface change: modified port DataElement, signal, CAN message, BSW config.
   - Calibration change: parameter value only, no code change.
   - Safety-relevant change: any change touching an ASIL-tagged element.
3. **Identify affected elements**: every SWC, BSW module, ARXML file, header, test case, requirement that needs to change. Reference `CODEBASE_MAP.md`.
4. **Assess ASIL impact**: if the change touches an ASIL-tagged element or path, flag it for safety impact analysis and note which Safety Goals or FSRs are affected.
5. **Produce an implementation plan**: ordered tasks, owner hints, complexity (S/M/L), dependencies.
6. **Define the test plan delta**: new tests needed, existing tests to rerun, regression scope.
7. **Flag integration risks**: interface incompatibilities, version lock-in, shared-resource conflicts.

### Impact analysis

1. **Identify the change origin**: the specific element changing (function, SWC port, BSW config parameter, data type, constant, ARXML element).
2. **Trace direct impacts** (must change):
   - Port DataElement type change -> all connected sender/receiver ports, ComSpecs, generated RTE code.
   - Function signature change -> all callers, all headers, all test stubs.
   - BSW config change (e.g., Dem event ID) -> SWC code, test cases, DTC documentation.
   - ASIL-tagged element change -> corresponding safety requirement, its test case, safety case.
3. **Trace indirect impacts** (must review or retest, not necessarily change):
   - SWCs consuming the output of a changed SWC.
   - Integration tests covering the changed signal path.
   - Calibration data referencing the changed parameter.
   - Timing budget affected by a changed runnable period.
4. **Assign regression scope**: **Minimal** (directly changed items only), **Targeted** (direct + signal path), **Full** (entire module or feature).
5. **Flag open-loop impacts**: changes where the effect cannot be determined without runtime data (e.g., calibration threshold change on a real vehicle).

## Input expected

- **CR analysis**: change request text / ticket / brief; optionally affected SWC name, current SW version, deadline, `CODEBASE_MAP.md`.
- **Impact analysis**: description of the change (what element is changing and how); optionally affected SWC name, `CODEBASE_MAP.md`, existing requirement and test case IDs.

## Output format

### CR analysis

~~~
## Change Request Analysis: <CR Title>

### Change Classification
[Type, ASIL impact: Yes/No, scope: Localized / Cross-cutting]

### Affected Elements
| Element | Type | Change Needed | Complexity |
|---------|------|---------------|------------|
...

### Safety Impact
[None / Affected safety goal or FSR + required actions per ISO 26262-8 section8.4]

### Implementation Plan
| # | Task | Owner Hint | Complexity | Depends On |
|---|------|------------|------------|------------|
...

### Test Plan Delta
| Test Case | Action | Rationale |
|-----------|--------|-----------|
...

### Integration Risks
- [Risk and mitigation]
~~~

### Impact analysis

~~~
## Change Impact Analysis: <Change Description>

### Change Origin
[Element, layer, nature of change]

### Direct Impacts (must change)
| Element | Type | Required Change |
|---------|------|-----------------|
...

### Indirect Impacts (must review / retest)
| Element | Type | Review / Retest Action |
|---------|------|------------------------|
...

### Safety Impact
[None / ASIL-tagged elements affected + required actions]

### Regression Scope Recommendation
[Minimal / Targeted / Full -- with rationale]

### Open-Loop Impacts
[Items that cannot be assessed without runtime data]
~~~

## Change Request Analysis: CR-0088 -- Lower Low-Voltage Warning Threshold

### Change Classification
Calibration/functional change. ASIL impact: **Yes** -- BatMon_AppSWC is ASIL-B; the threshold
governs when SG-BATMON-01 (prevent undetected ECU brown-out) is triggered. Scope: localized to
BatMon, but with safety-case impact.

### Affected Elements
| Element                       | Type           | Change Needed                              | Complexity |
|-------------------------------|----------------|--------------------------------------------|------------|
| `BATMON_LOW_THRESH_MV` macro  | C source       | Change 11500 -> 11000                       | S          |
| SW-REQ-BATMON-002             | Requirement    | Update threshold value and cold-weather rationale | S    |
| TC-BATMON-002                 | Test case      | Update expected threshold in boundary tests | S         |
| BatMon calibration data sheet | Documentation  | Update nominal value                       | S          |
| HARA / safety goal check      | Safety         | Verify new threshold does not violate SG   | M          |

### Safety Impact
SW-REQ-BATMON-002 carries ASIL-B, inherited from SG-BATMON-01. Lowering the threshold from
11.5 V to 11.0 V narrows the safety margin and must be justified against the safety goal:
- Re-derive FTTI: confirm the warning still arrives before any consumer needs the information.
- Confirm 11.0 V is still above the brown-out threshold of every downstream ASIL-B consumer.
- Update the safety case to record the threshold change and its rationale (ISO 26262-8 section8.4).
- Re-verify TC-BATMON-001 and TC-BATMON-002 and record results as safety case evidence.

### Implementation Plan
| # | Task                                                                  | Owner Hint  | Complexity | Depends On |
|---|-----------------------------------------------------------------------|-------------|------------|------------|
| 1 | Verify downstream consumers of LowVoltageWarning_Active (CODEBASE_MAP / ARXML) | Safety eng | S | --         |
| 2 | Update `BATMON_LOW_THRESH_MV` in `BatMon_App.h`                       | SW dev      | S          | Task 1     |
| 3 | Update SW-REQ-BATMON-002 with new threshold and cold-weather rationale| Req eng     | S          | Task 1     |
| 4 | Update TC-BATMON-002 boundary test inputs                             | Test eng    | S          | Task 2     |
| 5 | Re-run TC-BATMON-002 and TC-BATMON-001 regression                     | Test eng    | S          | Task 4     |
| 6 | Update calibration data sheet                                         | SW dev      | S          | Task 2     |

### Test Plan Delta
| Test Case     | Action | Rationale                                            |
|---------------|--------|------------------------------------------------------|
| TC-BATMON-002 | Update | Threshold boundary value changes from 11500 to 11000 |
| TC-BATMON-001 | Rerun  | Regression -- verify accuracy test still passes       |
| TC-BATMON-004 | Rerun  | Regression -- quiescent current unaffected but confirm|

### Integration Risks
- Safety case update is required before release (ISO 26262-8 section8.4) -- captured as Task 1.
- Cold-weather validation: the new 11.0 V threshold should be validated in a climate chamber
  test at  30 degC with the actual battery cell chemistry before mass production release.
- ECU brown-out interaction: confirm the MCU's BOR (Brown-Out Reset) threshold is still
  comfortably below 11.0 V after accounting for harness drop and regulator dropout.
~~~

### Example 2 -- Impact analysis

**Input:**
Change: rename the AUTOSAR DataElement `Voltage_mV` to `BattVoltage_mV` in the
`BattVoltageIf` SenderReceiver interface. Affects BatMon_AppSWC (provider) and
DisplayCtrl_AppSWC (consumer).

**Output:**
~~~
## Change Impact Analysis: Rename DataElement Voltage_mV -> BattVoltage_mV

### Change Origin
ARXML SenderReceiver interface `BattVoltageIf`, DataElement short-name.
Layer: Application SWC interface / RTE contract.

### Direct Impacts (must change)
| Element                                            | Type      | Required Change                                              |
|----------------------------------------------------|-----------|--------------------------------------------------------------|
| `BattVoltageIf` ARXML (interface definition)       | ARXML     | Rename `<SHORT-NAME>Voltage_mV</SHORT-NAME>` -> `BattVoltage_mV` |
| `BatMon_AppSWC` ARXML (provided port ComSpec)      | ARXML     | Update `<DATA-ELEMENT-REF>` to `BattVoltage_mV`              |
| `DisplayCtrl_AppSWC` ARXML (required port ComSpec) | ARXML     | Update `<DATA-ELEMENT-REF>` to `BattVoltage_mV`              |
| Generated `Rte_BatMon_AppSWC.h`                    | Generated | Regenerate -- `Rte_Write_PBattVoltage_BattVoltage_mV()`       |
| Generated `Rte_DisplayCtrl_AppSWC.h`               | Generated | Regenerate -- `Rte_Read_RBattVoltage_BattVoltage_mV()`        |
| `BatMon_App.c` RTE API call                        | C source  | Update `Rte_Write_PBattVoltage_Voltage_mV` -> `_BattVoltage_mV`|
| `DisplayCtrl_App.c` RTE API call                   | C source  | Update `Rte_Read_RBattVoltage_Voltage_mV` -> `_BattVoltage_mV`|
| SW-REQ-BATMON-001                                  | Requirement | Update DataElement name in interface reference            |
| TC-BATMON-001, TC-DISPLAY-003                      | Test cases | Update stub API name in test harness                       |

### Indirect Impacts (must review / retest)
| Element                         | Type         | Action                                                  |
|---------------------------------|--------------|---------------------------------------------------------|
| `VehicleComposition` ARXML      | ARXML        | Verify connector references remain valid after rename   |
| Integration test suite (BatMon) | Test         | Full retest of battery monitoring signal path           |
| Calibration tool signal mapping | Tool config  | Update signal name in CANape/INCA measurement config    |

### Safety Impact
**Required** -- `BattVoltageIf` carries ASIL-B (allocated from SG-BATMON-01: prevent undetected
ECU brown-out). A safety impact assessment per ISO 26262-8 section8.4 is required.
- Confirm the rename is semantics-preserving (it is -- same type, range, units, semantics).
- Re-verification: TC-BATMON-001/002 and TC-DISPLAY-003 must be re-executed and recorded in
  the safety case as evidence for SW-REQ-BATMON-001.
- Configuration management: interface ARXML revision must be documented under change control
  per ISO 26262-8 section7.

### Regression Scope Recommendation
**Targeted** -- run the BatMon signal path integration tests (BatMon -> DisplayCtrl chain)
plus a build verification of both SWCs, and re-execute the ASIL-B test cases for the
safety case. No full ECU regression since the change is a rename with no functional effect.

### Open-Loop Impacts
None -- pure rename, no functional effect. No runtime validation beyond build and integration test is required.
~~~

