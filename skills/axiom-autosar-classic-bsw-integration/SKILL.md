---
name: axiom-autosar-classic-bsw-integration
title: AUTOSAR Classic BSW Integration
description: >
  Integrates and reviews AUTOSAR Classic BSW configuration (ARXML/BMD/RTE/OS/COM/PduR/CanIf/CanTp/Dcm/Dem/NvM/EcuM) and produces an integration report with severity-ranked findings and a validation matrix.
version: 0.1.0
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
  standards: [AUTOSAR Classic R24-11, ISO 26262:2018]
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
