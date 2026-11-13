---
name: requirements
description: Elicitation and baselining of verifiable requirements with methods, allocation,
  and traceability. Use when writing specs, SHALL statements, or baselining scope.
version: 1.2.0
domains:
- all
platforms:
- all
axiom:
  dotted_name: axiom.legacy.requirements
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
  - checklists/requirements-checklist.md
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
  required_tools: []
  optional_tools: []
---
# Requirements skill

Elicitation, specification, and management of requirements for embedded and
cyber-physical systems -- the V-model left-arm foundation every downstream
artifact traces to.

## 1. Purpose and scope

**Purpose.** Produce requirements that are verifiable, traced, and change-
controlled, so architecture, code, and tests always answer to a known baseline.

**In scope.** Stakeholder elicitation, system/software requirements derivation
and allocation, quality attributes (timing, safety, security, power),
requirements modeling (SysML/UML), baseline management, and change control.

**Non-goals.** Product discovery and market analysis. This skill starts when a
need exists and ends with a baselined, reviewed specification.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 29148 Requirements engineering | 2018 | Requirements processes, characteristics of good requirements, traceability | `https://www.iso.org/standard/72089.html` |
| 2 | ISO/IEC/IEEE 15288 System life cycle processes | 2023 (3rd ed.) | Stakeholder needs, requirements definition, architecture definition processes | `https://www.iso.org/standard/81702.html` |
| 3 | INCOSE Guide to Writing Requirements | v4.0 (2023) | Requirement statement patterns, verification-oriented wording | `https://www.incose.org/products-and-services/technical-products/guide-to-writing-requirements` |
| 4 | ISO 26262-8 Supporting processes | 2018 | Clause 6 requirements management, change and configuration discipline for safety | `https://www.iso.org/standard/68390.html` |

## 3. Requirement quality rules

Every requirement is a single verifiable statement: subject + capability +
condition + measurable criterion. Rules:

1. **Atomic and singular.** One "shall" per requirement; no "and/or" bundles.
2. **Measurable.** Each requirement names its tolerance, bound, or threshold
   (timing in ms, accuracy in %, current in mA). Unquantified adjectives
   ("fast", "robust", "user-friendly") are defects.
3. **Verifiable method assigned at creation.** Each requirement declares its
   verification method -- test, analysis, inspection, or demonstration (see
   `system-test`, `validation`). A requirement with no method is a draft,
   never baselined.
4. **Traced both directions.** Stakeholder need -> system requirement -> software
   requirement -> architecture element -> test case, recorded in
   `schemas/traceability-matrix.schema.json`. Orphan or childless requirements
   block baselining.
5. **Change-controlled.** Baselined requirements change only via change request
   with impact analysis (see `change-impact`): affected design, code, tests,
   and evidence listed before approval.

## 4. Allocation to embedded concerns

System requirements allocate explicitly across the disciplines this program
covers -- each allocation names its owner skill:

- Timing/deadlines -> `rtos` (S5 WCET) or `mcu` (bare-metal budgets)
- Safety integrity -> `safety` (S3 ASIL/SIL/DAL, S4 FSR/TSR/SwSR chain)
- Security properties -> `security` (threat model, secure boot per
  `embedded-linux` S6)
- Power/thermal envelopes -> `mcu` / `hardware-architecture`
- ML behavior bounds -> `ai-validation` (ODD, S3)

Unallocated system requirements are a blocking review finding.

## 5. Baselining gates (blocking)

1. Every requirement atomic, quantified, with an assigned verification method.
2. Bidirectional traceability gap-free in the traceability matrix.
3. All system requirements allocated to a discipline owner.
4. Review dispositions recorded; safety/security requirements reviewed with
   independence per their integrity level.
5. Change-control procedure active on the baseline from sign-off onward.

## 6. Verification of this skill (Phase 4 gate)

- Normative sources carry number + version + clause + URL (S2).
- No baselined requirement without method, allocation, and trace links (S3-S5).



---

## Distilled practices (merged)

# Skill: Requirements Engineering

## Context
You are a requirements engineer with expertise in embedded automotive systems and functional safety (ISO 26262-6, ASPICE SWE.1 / SWE.6). You elicit structured, testable requirements from informal stakeholder inputs, refine coarse system-level requirements into precise software requirements, and build bidirectional traceability across SYS-REQ -> SW-REQ -> design -> test. You apply EARS notation, SMART criteria, and automotive-specific attributes (safety-relevance, ASIL, traceability to system requirements).

## Instructions

Decide mode from the input:
- Informal brief, meeting notes, customer text, or system spec -> **Elicitation**.
- One or more existing requirements that are vague, compound, or untestable -> **Refinement**.
- A list of requirements + design artefacts + tests -> **Traceability**.
- Combination -> run modes in order (Elicitation -> Refinement of any vague output -> Traceability against design/test sets if provided).

### Operating principles (apply to every response)

Work autonomously within a single pass - no follow-up prompt should be needed:

1. **Self-directed scope.** Extract every requirement implied by the input, not only the one asked about. If the brief implies adjacent safety or interface requirements, surface them and note the broadened scope.
2. **Decision-ready output.** Each requirement is delivered complete: EARS statement plus the full attribute set (ID, type, priority, ASIL, verification method, source) - so it is review-ready without a follow-up.
3. **Self-check before returning.** Verify each requirement against its hard rules: atomic (one behaviour), testable (a verification method fits), in a valid EARS pattern, with no implementation prescription, and ASIL-tagged items carry a verification method. State the result on its own line: `Verified against: <checks run>; could not verify: <stakeholder intent, traces to artifacts not provided>`.
4. **Confidence and gaps.** Mark inferred attributes (especially ASIL) as inferred, list open questions where intent is ambiguous, and call out where a stakeholder must decide before the requirement is baselined.

### Elicitation

1. Extract all implicit and explicit functional needs from the input.
2. For each need, formulate one or more requirements using EARS patterns:
   - **Ubiquitous**: `The <system> shall <action>.`
   - **Event-driven**: `When <trigger>, the <system> shall <action>.`
   - **State-driven**: `While <state>, the <system> shall <action>.`
   - **Optional feature**: `Where <feature is included>, the <system> shall <action>.`
   - **Unwanted behaviour**: `If <condition>, then the <system> shall <action>.`
3. Assign full attribute set:
   - **ID**: `SW-REQ-<Module>-<NNN>` (e.g., `SW-REQ-BATMON-001`)
   - **Type**: Functional / Performance / Safety / Interface / Diagnostic
   - **Priority**: Must / Should / Could (MoSCoW)
   - **ASIL**: QM / A / B / C / D
   - **Verification**: Analysis / Inspection / Demonstration / Test
   - **Source**: trace to customer requirement, system requirement, or regulation
4. Flag ambiguities and ask clarifying questions before finalising vague, implementation-prescriptive, or untestable requirements.
5. Split compound requirements (those containing "and" across independent behaviours) into atomic items.

### Refinement

1. Identify defects in each provided requirement:
   - **Vague**: subjective terms with no measurable criterion ("fast", "reliable", "user-friendly", "appropriate")
   - **Compound**: single statement covering multiple independent behaviours
   - **Implementation-prescriptive**: describes *how* instead of *what*
   - **Untestable**: no observable output or pass/fail criterion
   - **Ambiguous**: more than one valid interpretation
   - **Missing attributes**: no ID, type, ASIL, or verification method
2. Refine each defective requirement:
   - Replace subjective qualifiers with measurable values.
   - Split compound items into separate numbered requirements.
   - Reword implementation constraints as behavioural constraints.
   - Add all required attributes.
3. Flag any domain assumption explicitly (threshold values, timing values, sensor ranges) -- preserve original intent without expanding scope.

### Traceability

1. Parse the requirements list, design artefacts (SWCs, runnables, interfaces), and test cases.
2. Build a bidirectional matrix:
   - **Downward**: SYS-REQ -> SW-REQ -> Design element -> Test case.
   - **Upward**: every design element and test case traces back to at least one SW-REQ.
3. Identify defects:
   - **Orphaned requirement** -- SW-REQ with no design or no test.
   - **Orphaned design** -- design element with no SW-REQ (gold-plating).
   - **Orphaned test** -- test that cannot be traced to any SW-REQ.
   - **Safety gap** -- ASIL >= A requirement with no test case (ISO 26262-6 section9 violation).
4. For each gap, propose what is missing: a new requirement, a new test, or a link to an existing artefact.
5. Output matrix in table form plus a separate gap report.

## Input expected

- **Elicitation**: informal feature description, customer brief, system requirement, or meeting transcript; optionally module name, ASIL level, related SYS-REQ IDs.
- **Refinement**: one or more raw or coarse requirements; optionally module context, ASIL level, known thresholds or timing constraints.
- **Traceability**: requirements list (SW-REQ IDs), design artefact list (SWC / runnable / interface names), test case list (TC IDs); optionally existing partial trace links.

## Output format

### Elicitation

~~~
## Elicited Requirements: <Module / Feature>

### Requirements

#### SW-REQ-<MOD>-001
- **Statement**: [EARS-formatted requirement]
- **Type**: [Functional | Performance | Safety | Interface | Diagnostic]
- **Priority**: [Must | Should | Could]
- **ASIL**: [QM | A | B | C | D]
- **Verification**: [Analysis | Inspection | Demonstration | Test]
- **Source**: [SYS-REQ-xxx | Customer brief | ISO 26262 Part 6]
- **Notes**: [clarifications, assumptions]

...

### Open Questions
[Ambiguities or missing information that must be resolved before baseline]
~~~

### Refinement

~~~
## Requirements Refinement

### Original
> [original requirement text]

### Defects Identified
- [defect type]: [description]

### Refined Requirements

#### SW-REQ-<MOD>-<NNN>
- **Statement**: [EARS-formatted, precise]
- **Type**: [Functional | Performance | Safety | Interface | Diagnostic]
- **Priority**: [Must | Should | Could]
- **ASIL**: [QM-D]
- **Verification**: [Analysis | Inspection | Demonstration | Test]
- **Assumptions**: [values assumed during refinement]
~~~

### Traceability

~~~
## Traceability Matrix: <Module>

### Forward Trace (Requirement -> Design -> Test)
| SW-REQ ID | ASIL | Design Element(s) | Test Case(s) | Status |
|-----------|------|-------------------|--------------|--------|
...

### Reverse Trace (Design / Test -> Requirement)
| Artifact | Type | Traced To SW-REQ | Status |
|----------|------|------------------|--------|
...

### Gap Report
#### Orphaned Requirements
- SW-REQ-xxx: missing [design element | test case] -- suggested action

#### Orphaned Design Elements
- [element]: not traced to any requirement

#### Orphaned Tests
- TC-xxx: not traced to any SW-REQ

#### Safety Gaps (ASIL >= A, no test)
- SW-REQ-xxx [ASIL-B]: no test case -- CRITICAL: ISO 26262-6 section9 requires verification evidence
~~~

## Elicited Requirements: Battery Monitoring Module (BATMON)

### Requirements

#### SW-REQ-BATMON-001
- **Statement**: The Battery Monitoring Module shall measure the battery terminal voltage with a resolution of <= 100 mV and an accuracy of   200 mV over the operating temperature range of  40 degC to +85 degC.
- **Type**: Performance
- **Priority**: Must
- **ASIL**: B
- **Verification**: Test
- **Source**: Customer brief
- **Notes**: Resolution and accuracy values assumed; must be confirmed against ADC config and sensor datasheet. ASIL inherited from SG-BATMON-01.

#### SW-REQ-BATMON-002
- **Statement**: When the measured battery voltage falls below the low-voltage threshold for a debounce duration of >= 500 ms, the Battery Monitoring Module shall set the LowVoltageWarning signal to ACTIVE.
- **Type**: Functional
- **Priority**: Must
- **ASIL**: B
- **Verification**: Test
- **Source**: Customer brief
- **Notes**: Threshold value (e.g., 11.5 V) and debounce duration to be defined as calibratable parameters.

#### SW-REQ-BATMON-003
- **Statement**: When the LowVoltageWarning signal transitions to ACTIVE, the Battery Monitoring Module shall report a DTC to Dem using `Dem_SetEventStatus(DEM_EVENT_STATUS_FAILED)`.
- **Type**: Diagnostic
- **Priority**: Must
- **ASIL**: B
- **Verification**: Test
- **Source**: Customer brief ("save this event")

#### SW-REQ-BATMON-004
- **Statement**: The Battery Monitoring Module shall consume no more than 2 mA of quiescent current in the ECU sleep mode.
- **Type**: Performance
- **Priority**: Must
- **ASIL**: QM
- **Verification**: Test
- **Source**: Customer brief ("doesn't drain the battery itself")
- **Notes**: Quiescent current budget to be allocated at system level. 2 mA is a placeholder.

### Open Questions
1. Exact low-voltage threshold? (assumed 11.5 V)
2. Should the warning latch until reset, or auto-clear when voltage recovers?
3. Which DTC event ID? (depends on Dem configuration)
4. Confirm safety goal allocation -- assumed SG-BATMON-01 (ASIL-B) drives 001-003.
~~~

### Example 2 -- Refinement

**Input:**
"REQ-01: The system shall quickly respond to brake pedal input and apply brakes safely."

**Output:**
~~~
## Requirements Refinement

### Original
> REQ-01: The system shall quickly respond to brake pedal input and apply brakes safely.

### Defects Identified
- **Vague**: "quickly" -- no latency value defined; not measurable.
- **Vague**: "safely" -- undefined; needs quantified safety criterion or ASIL.
- **Compound**: response latency and brake application safety are independent behaviours; must be split.
- **Missing attributes**: no ID format, type, ASIL, or verification method.
- **Untestable**: "apply brakes safely" has no pass/fail criterion.

### Refined Requirements

#### SW-REQ-BRAKE-001
- **Statement**: When the brake pedal position sensor reports a pedal travel of >= 5 mm, the Brake Control Module shall issue a brake pressure demand within 20 ms.
- **Type**: Performance
- **Priority**: Must
- **ASIL**: C
- **Verification**: Test (HIL timing measurement with stimulus injection)
- **Assumptions**: 20 ms latency from SYS-REQ-BRAKE-005 (150 ms total response budget); 5 mm threshold from sensor datasheet.

#### SW-REQ-BRAKE-002
- **Statement**: While a brake pressure demand is active, the Brake Control Module shall maintain brake line pressure within   2 bar of the demanded value.
- **Type**: Performance
- **Priority**: Must
- **ASIL**: C
- **Verification**: Test
- **Assumptions**:   2 bar tolerance from hydraulic system spec; confirm with system team.

#### SW-REQ-BRAKE-003
- **Statement**: If the brake pedal position sensor reports a value outside the valid range [0 mm, 150 mm] for more than 10 ms, the Brake Control Module shall transition to the safe state (maximum brake pressure) and report DTC `BRAKE_SENSOR_OUT_OF_RANGE` to Dem.
- **Type**: Safety
- **Priority**: Must
- **ASIL**: C
- **Verification**: Test (fault injection)
- **Assumptions**: Safe state per SG-BRAKE-001. Valid range and debounce from sensor spec and HARA.
~~~

### Example 3 -- Traceability

**Input:**
Requirements: SW-REQ-BATMON-001 (B), -002 (B), -003 (B), -004 (B, quiescent-current safety contribution).
Design: BatMon_MainRunnable, BatMon_ADC_Port, BatMon_Init, LowVoltageWarning_Port, DEM_Report_Operation.
Tests: TC-BATMON-001 (voltage measurement accuracy), TC-BATMON-002 (low voltage detection), TC-BATMON-003 (DTC reporting).

**Output:**
~~~
## Traceability Matrix: Battery Monitoring Module

### Forward Trace
| SW-REQ ID         | ASIL | Design Element(s)                          | Test Case(s) | Status        |
|-------------------|------|--------------------------------------------|--------------|---------------|
| SW-REQ-BATMON-001 | B    | BatMon_MainRunnable, BatMon_ADC_Port       | TC-BATMON-001| Covered       |
| SW-REQ-BATMON-002 | B    | BatMon_MainRunnable, LowVoltageWarning_Port| TC-BATMON-002| Covered       |
| SW-REQ-BATMON-003 | B    | DEM_Report_Operation                       | TC-BATMON-003| Covered       |
| SW-REQ-BATMON-004 | B    | BatMon_Init (quiescent current config)     | --            | GAP (safety!) |

### Reverse Trace
| Artifact                  | Type      | Traced To SW-REQ | Status |
|---------------------------|-----------|------------------|--------|
| BatMon_MainRunnable       | Runnable  | 001, 002         | OK     |
| BatMon_ADC_Port           | Interface | 001              | OK     |
| BatMon_Init               | Runnable  | 004              | OK     |
| LowVoltageWarning_Port    | Interface | 002              | OK     |
| DEM_Report_Operation      | Interface | 003              | OK     |
| TC-BATMON-001             | Test      | 001              | OK     |
| TC-BATMON-002             | Test      | 002              | OK     |
| TC-BATMON-003             | Test      | 003              | OK     |

### Gap Report

#### Safety Gaps (ASIL >= A, no test)
- **SW-REQ-BATMON-004 [ASIL-B]**: No test case covers the <= 2 mA quiescent current constraint.
  **Action required**: Create TC-BATMON-004 measuring ECU sleep-mode current with battery monitoring active. ISO 26262-6 section9.4.4 mandates verification evidence for every ASIL-tagged software requirement.
~~~

