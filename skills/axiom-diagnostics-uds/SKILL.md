---
name: axiom-diagnostics-uds
title: UDS Diagnostics Design and Validation
description: >
  Designs UDS service coverage, session/security posture and negative-response matrices, and validates them with a deterministic checker script.
version: 0.1.0
author: PRATIK PATIL
license: Apache-2.0
domains: [automotive]
platforms: [mcu, mpu, autosar-classic, autosar-adaptive]
axiom:
  dotted_name: axiom.automotive.diagnostics.uds
  domain: automotive
  subdomain: diagnostics
  category: verification
  maturity: beta
  owner: axiom-embedded
  tags: [diagnostics]
  related_skills: [axiom-diagnostics-doip, axiom-autosar-classic-bsw-integration]
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [ISO 14229-1, ISO 26262:2018]
  artifact_types: [diagnostic requirements, service matrix, validation report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom UDS Diagnostics Design and Validation (exemplar)

## Purpose
Design UDS service coverage (sessions, security, addressing) and validate it with a deterministic matrix checker, producing diagnostic requirements, a service matrix, and a validation report. Original AxiomEmbedded method; builds on (does not duplicate) the existing `automotive-diagnostics` skill and its extract-driven generator.

## When to Use
- A new ECU diagnostic server or tester matrix must be designed or reviewed.
- UDS coverage gaps or NRC handling must be checked before release.

## When Not to Use
- As type-approval or homologation proof; produce evidence for qualified review.
- When service_identifiers are invented instead of sourced from the extract/spec.

## Required Inputs
- `uds_matrix.yaml`: services list with `sid`, `sessions`, optional `dids`/`subfunctions` (see `templates/uds-matrix.template.yaml`).
- `objective`: design or review goal.

## Optional Inputs
- ODX/DECT source references; prior validation reports.

## Prerequisites
- `automotive-diagnostics` skill available for deep generator flows; PyYAML for the checker.

## Execution Workflow
1. Normalize request into service scope (SIDs, sessions, security levels).
2. Author or ingest `uds_matrix.yaml` from the extract (never invent SIDs).
3. Run `scripts/check_uds_matrix.py <dir>`; fix missing required SIDs (0x10/0x22/0x19/0x27/0x3E) and session gaps.
4. Design negative-response coverage per service (wrong session, locked access, unknown selector).
5. Review session/security posture (S3 timeout, lockout timing, test-key hygiene).
6. Emit validation report + traceability rows (requirement -> SID -> case -> evidence).
7. Dry-run `run_skill` then write artifacts under the run dir.

## Tool Invocations
- `run_skill{skill_id: axiom-diagnostics-uds, dry_run: true}` first.
- `validate_skill{skill_id}` gates release.

## Decision Rules
- Missing required SID = major finding; unsupported SID needs explicit exclusion.
- Service without session declaration = major; without negative tests = minor.
- Production image with test keys = blocker.

## Workflow
As Execution Workflow above; checker output is the primary evidence input.

## Deliverables
- `diagnostic-requirements.md` (service/DID/session/security catalogue).
- `uds-matrix.yaml` (canonical matrix, provenance header).
- `validation-report.md` (checker results + triage + next actions).
- Run manifest under `.axiom/runs/<ts>/axiom-diagnostics-uds/`.

## Acceptance Criteria
- Required SIDs present or explicitly excluded with rationale.
- Every service declares sessions; every gated service has negative cases.
- Checker executed; REVIEW items triaged; human review for security-relevant output.

## Acceptance
- Machine gates: checker exit 0 or triaged REVIEW + checklist green + sign-off.

## Validation Procedure
1. `python skills/axiom-diagnostics-uds/scripts/check_uds_matrix.py <dir>`.
2. `python scripts/validate_skills.py --skill axiom-diagnostics-uds`.
3. Checklist `checklists/review.yaml` green.

## Common Failure Modes
- Wrong-session access returns wrong NRC -> fix dispatch order (format -> session -> security -> conditions -> resource).
- Seed/key lockout untested -> add timing test with NVM counter proof.
- Functional addressing returns NRCs on bus -> suppress responses per standard.

## Guardrails
- No production keys in source; test keys flagged TEST-ONLY and build-gated.
- Never claim type approval from heuristic checks.

## References
- ISO 14229 (landing: https://www.iso.org/search.html?q=14229).
- ISO 13400 (landing: https://www.iso.org/search.html?q=13400).
- ASAM ODX (landing: https://www.asam.net/standards/detail/mcd-2-d/).
