---
name: axiom-validation-levels
title: Validation Levels and Evidence Framework
description: Distinguishes source-level, build, static analysis, host-based, simulation,
  HIL and physical board acceptance validation; defines prerequisites, equipment,
  procedure, expected results, failure conditions, measurements, evidence format and
  limitations for each. Never reports compile success as hardware proof. Use when
  validation levels tasks arise in all projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains:
- all
platforms:
- mcu
- mpu
axiom:
  dotted_name: axiom.platform.validation.levels
  domain: platform
  subdomain: validation
  category: verification
  maturity: experimental
  owner: axiom-embedded
  tags:
  - validation
  - verification
  - hil
  - simulation
  - testing
  related_skills:
  - validation
  - simulation
  - test-automation
  - integration-test
  - axiom-mil-sil-hil-testing
  lifecycle:
  - requirements
  - architecture
  - design
  - implementation
  - integration
  - verification
  - validation
  - release
  standards: []
  artifact_types:
  - validation plan
  - evidence package
  - acceptance report
  mcp_tools:
  - run_skill
  - validate_skill
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs:
  - repository path
  - target files
  - objective
  - constraints
  outputs:
  - run report
  - run manifest
  required_tools:
  - validate_skill
  optional_tools:
  - run_skill
  checklists:
  - checklists/review.yaml
---
# Axiom Validation Levels and Evidence Framework

## Purpose
Distinguishes validation levels from source edits through physical board acceptance, and defines the
prerequisites, equipment, procedure, expected results, failure conditions, measurements, evidence format,
and limitations for each. Compile success is never reported as hardware proof. This skill is original
AxiomEmbedded content.

Scope: validation (platform). Maturity: experimental.

## When to Use
- The project needs a validation plan, evidence structure, or acceptance criteria across levels.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Requirements and acceptance criteria with traceability IDs.

## Optional Inputs
- Existing test plans, simulation models, HIL setups, prior evidence packages.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded (`validation`, `simulation`, `test-automation`, `integration-test`, `axiom-mil-sil-hil-testing`).

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing validation artifacts.
3. Select validation levels per requirement criticality.
4. Generate or modify artifacts (dry-run first).
5. Validate structurally and semantically (scripts/ + checklists/).
6. Run applicable checks; record results.
7. Produce traceability and review evidence.
8. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer explicit configuration over invented defaults; flag every assumption.
- Safety/security-relevant outputs require human review (review_required: true).

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Validation levels

### 1. Source-level validation
- **Prerequisites**: requirements IDs, coding standard, review checklist.
- **Equipment**: none (editor/review).
- **Procedure**: review diff against requirements; check naming, contracts, traceability.
- **Expected result**: all review comments resolved or deferred with rationale.
- **Failure conditions**: missing traceability, undocumented assumptions, scope creep.
- **Measurement**: review coverage, number of findings by severity.
- **Evidence format**: review record with diff hash, reviewer, date, findings.
- **Limitations**: cannot prove runtime behavior or hardware interaction.

### 2. Build validation
- **Prerequisites**: toolchain, build scripts, dependency lock.
- **Equipment**: build host.
- **Procedure**: clean configure + compile + link for all targets/configs.
- **Expected result**: zero errors; warnings within agreed budget.
- **Failure conditions**: compile/link errors, missing symbols, config drift.
- **Measurement**: build time, warning count, binary size.
- **Evidence format**: build log, artifact hashes, config snapshot.
- **Limitations**: compile success is not functional or hardware proof.

### 3. Static analysis
- **Prerequisites**: static analyzer config, rule set (MISRA/CERT), baseline.
- **Equipment**: analysis host/CI.
- **Procedure**: run analyzer; triage findings; document deviations.
- **Expected result**: zero mandatory/required violations or approved deviations.
- **Failure conditions**: new high-severity findings, suppressed rules without rationale.
- **Measurement**: finding counts by severity/rule, suppression count.
- **Evidence format**: analyzer report, triage log, deviation records.
- **Limitations**: heuristic; cannot detect all runtime faults or timing issues.

### 4. Host-based testing
- **Prerequisites**: unit/integration test framework, mocks/stubs for hardware.
- **Equipment**: host machine.
- **Procedure**: run tests on host with emulated hardware boundaries.
- **Expected result**: all tests pass; coverage meets target.
- **Failure conditions**: failures, flaky tests, coverage shortfalls.
- **Measurement**: pass/fail counts, coverage percentages, execution time.
- **Evidence format**: test report, coverage report, seed/config.
- **Limitations**: host timing and hardware behavior differ from target.

### 5. Simulation
- **Prerequisites**: plant/model, simulation environment, interfaces.
- **Equipment**: simulator host, models.
- **Procedure**: run MIL/SIL scenarios including faults and boundaries.
- **Expected result**: requirements met within tolerances; no unhandled faults.
- **Failure conditions**: requirement violations, model divergence, crashes.
- **Measurement**: KPIs, error metrics, scenario coverage.
- **Evidence format**: simulation report, scenario list, model version.
- **Limitations**: model fidelity limits; not a substitute for hardware.

### 6. Hardware-in-the-loop (HIL)
- **Prerequisites**: HIL rig, I/O mapping, plant model, test scripts.
- **Equipment**: HIL bench, real ECU/target, measurement devices.
- **Procedure**: execute automated tests with real hardware in closed loop.
- **Expected result**: all scenarios pass within tolerances and timing.
- **Failure conditions**: timing violations, I/O mismatches, safety trips.
- **Measurement**: latency, jitter, error rates, resource usage.
- **Evidence format**: HIL log, trace captures, pass/fail summary.
- **Limitations**: rig approximates real environment; calibration drift possible.

### 7. Physical board acceptance
- **Prerequisites**: acceptance plan, calibrated equipment, environmental conditions.
- **Equipment**: board under test, probes, power supply, environmental chamber (as needed).
- **Procedure**: execute acceptance tests on the physical board in target conditions.
- **Expected result**: all acceptance criteria met; no critical defects.
- **Failure conditions**: any acceptance criterion failure or safety issue.
- **Measurement**: electrical parameters, timing, environmental margins.
- **Evidence format**: signed acceptance report, raw measurements, photos/captures.
- **Limitations**: costly and late; findings may require redesign.

## Cross-level rules
- Never report build success as hardware proof.
- Each level's evidence must cite requirement IDs and level.
- Failures at a lower level block higher-level claims.
- Record environment, versions, and configuration for reproducibility.
- Keep acceptance criteria measurable and unambiguous.

## Deliverables
- Validation plan mapping requirements to levels.
- Evidence package per level with measurements and limitations.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-validation-levels`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.
- Reporting compile success as hardware proof -> explicitly forbidden.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `validation`, `simulation`, `test-automation`, `integration-test`, `axiom-mil-sil-hil-testing`.
