---
name: axiom-interface-contract-design
title: Interface Contract Design
description: >
  Designs versioned interface contracts between software components and subsystems
  (signals, services, APIs, diagnostic ports), with compatibility checks and
  traceability from requirements to integration tests.
version: 0.1.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.cross-domain.interface.contract.design
  domain: cross-domain
  subdomain: architecture
  category: design
  maturity: experimental
  owner: axiom-embedded
  tags: [interface, contract, architecture, traceability]
  related_skills: [axiom-platform-architecture-review, axiom-architecture-decision-records]
  lifecycle: [requirements, architecture, design, integration, verification]
  standards: []
  artifact_types: [interface contract, compatibility report]
  mcp_tools: [run_skill, validate_skill, generate_checklist, generate_traceability_matrix]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill, generate_traceability_matrix]
---

# Axiom Interface Contract Design

## Purpose
Define exact, versioned contracts for every interface a component exposes or consumes —
function signatures, message/signal layouts, service operations, timing and error
semantics — so integration failures become contract violations caught at review time,
not debug sessions. Produces an interface contract plus a compatibility report against
the actual implementation.

## When to Use
- Two teams or components integrate across a defined boundary (SWC-to-SWC, app-to-BSW,
  node-to-node, ECU-to-tester).
- An interface changes and consumers must be assessed for breakage.
- Recurring integration defects trace back to undocumented assumptions.

## When Not to Use
- As certification evidence on its own; contracts support, but never replace,
  qualified safety/security review.
- When no consumer or producer can be named — a contract with one side is fiction.

## Required Inputs
- Repository path and the target interface files (headers, IDLs, DBC/ARXML extracts,
  service manifests).
- Objective: which boundary is contracted and which version baseline applies.
- Constraints: compatibility policy (strict semver, backward-compatible-only, freeze).

## Optional Inputs
- Prior run manifests, existing ICD documents, integration test plans.

## Prerequisites
- `axiom doctor --skip-tests` green; `axiom-platform-architecture-review` loaded for
  system context.

## Execution Workflow
1. Normalize the request into boundary, direction (provided/required), and version baseline.
2. Inventory the boundary: enumerate every operation, signal, error code, and timing
   assumption from code and docs; record discrepancies between the two.
3. Draft the contract from `templates/interface-contract.template.yaml`: identity,
   version, each element with type, range, unit, default, error behavior, and owner.
4. Apply decision rules (sync vs async, versioning, error propagation) and record the
   rationale per rule.
5. Check compatibility: compare the draft contract against producers and consumers;
   every mismatch becomes a finding with severity, evidence location, and action.
6. Generate the traceability rows (requirement → contract element → test) via
   `generate_traceability_matrix` or by hand for small surfaces.
7. Dry-run review with owners; apply; re-run `validate_skill`.

## Tool Invocations
- `run_skill` with structured context; dry-run before writing contracts into the repo.
- `generate_traceability_matrix` for requirement → element → test rows.
- `validate_skill` must pass before the contract is declared binding.

## Decision Rules
- Synchronous call only when the caller can tolerate the worst-case blocking time;
  otherwise async with explicit queue-depth and overflow policy.
- Every contract carries a version and a changelog; breaking changes bump major and
  require consumer sign-off — no silent widening of ranges or reordering of fields.
- Error behavior is part of the contract: timeouts, invalid values, and init-order
  violations each map to a specified response, never to undefined behavior.
- Safety-related signals additionally require range plausibility and stale-data
  detection; flag them for human review.

## Workflow
Follow Execution Workflow; record per-step evidence (files inspected, decisions taken,
mismatches found) in the run manifest.

## Deliverables
- `interface-contract.yaml` (from template) under the agreed output directory.
- Compatibility report with findings ranked by severity.
- Run report + manifest under `.axiom/runs/<timestamp>/axiom-interface-contract-design/`.

## Acceptance Criteria
- Every boundary element has type, range, unit, default, and error behavior.
- Zero un-triaged mismatches between contract and implementation.
- Traceability rows complete for safety-related elements.

## Acceptance
- All checklist gates pass; owners of both sides have signed the contract version.

## Validation Procedure
- `validate_skill` passes; checklist gates green; contract parses against its template
  schema; consumer-owner review recorded.

## Common Failure Modes
- Undocumented units or byte order → require unit/endianness on every field; reject
  unit-less contracts.
- "Temporary" backdoor access bypassing the contract → list as a finding with removal date.
- Version drift between doc and code → single-source rule: code annotations generate
  the doc, or the doc is checked against code in CI.

## Guardrails
- No secrets in contracts or logs; no shell execution; no network calls.
- Never claim standards compliance from a contract review.

## References
- AUTOSAR Classic and Adaptive interface concepts (public specification landing pages).
- Project ICD and requirements baseline (project-local).
