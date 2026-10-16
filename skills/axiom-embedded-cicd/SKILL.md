---
name: axiom-embedded-cicd
title: Embedded CI-CD Pipeline Design
description: >
  Designs deterministic CI/CD pipelines for embedded repositories: build matrix,
  static checks, unit/integration tests, artifact versioning, and evidence
  packaging, delivered as a reviewable workflow fragment plus gate checklist.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.cross-domain.embedded.cicd
  domain: cross-domain
  subdomain: delivery
  category: release
  maturity: experimental
  owner: axiom-embedded
  tags: [cicd, pipeline, build, release, evidence]
  related_skills: [axiom-test-automation, axiom-automotive-release-readiness, axiom-hil-test-planning]
  lifecycle: [implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [pipeline definition, gate checklist, evidence package]
  mcp_tools: [run_skill, validate_skill, generate_checklist, generate_report, review_configuration]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill, review_configuration]
---

# Axiom Embedded CI-CD Pipeline Design

## Purpose
Give an embedded repository a pipeline that is reproducible, fast enough to run on
every push, and strict enough to gate releases: matrix builds per target, static
checks, unit tests on host, on-target or HIL stages where available, versioned
artifacts, and an evidence package the release skill can consume.

## When to Use
- A repo builds only on one engineer's machine or releases by hand.
- CI exists but is flaky, slow, or gates nothing.
- Release evidence must be produced automatically instead of assembled by hand.

## When Not to Use
- As a substitute for hardware testing strategy; the pipeline invokes HIL stages,
  it does not design them (see `axiom-hil-test-planning`).
- When build inputs are unpinned (floating toolchains); pin first, pipeline second.

## Required Inputs
- Repository path, target list (MCU/SoC, toolchain, build configs).
- Objective: push-gate vs nightly vs release pipeline (or all three).
- Constraints: runner types available, secret handling policy, artifact retention.

## Optional Inputs
- Existing workflow files, prior pipeline timing data, release evidence expectations.

## Prerequisites
- `axiom doctor --skip-tests` green; repository builds cleanly from a fresh clone.

## Execution Workflow
1. Normalize the request into pipeline tiers: push (fast, host-only), nightly
   (full matrix + target), release (gates + evidence + sign-off).
2. Inventory current build/test steps, durations, and flakiness; mark what must be
   hermetic (pinned toolchain, vendored or hashed dependencies).
3. Draft the workflow from `templates/ci-pipeline.template.yml`: jobs, matrix axes,
   caches, artifact uploads, and gate conditions per tier.
4. Define failure policy: which jobs block merge, which notify, retry limits, and
   the quarantine process for flaky tests (quarantine list, not silent skip).
5. Wire evidence: test reports, checker outputs, and version stamps collected as
   named artifacts feeding the release-readiness gate.
6. Validate the workflow file structurally (`review_configuration`) and dry-run the
   job list; apply; re-run `validate_skill`.

## Tool Invocations
- `run_skill` with structured context; dry-run before committing workflow files.
- `review_configuration` to parse and sanity-check the generated workflow YAML.
- `validate_skill` must pass before the pipeline is declared the release gate.

## Decision Rules
- Push tier stays under the agreed time budget (default 10 min) or it will be
  bypassed; move slow jobs to nightly, never delete their gates silently.
- Secrets live in the CI secret store, never in files; workflows reference names only.
- Flaky tests are quarantined with an owner and expiry, matching the triage skill's
  waiver discipline — never silently skipped.
- Release jobs run on protected branches with explicit approval; artifacts are
  immutable once published.

## Workflow
Follow Execution Workflow; record tier decisions, timing budgets, and gate mapping
in the run manifest.

## Deliverables
- Pipeline workflow file (from template, adapted) plus tier/gate documentation.
- Evidence-package layout consumed by `axiom-automotive-release-readiness`.
- Run report + manifest under `.axiom/runs/<timestamp>/axiom-embedded-cicd/`.

## Acceptance Criteria
- Push/nightly/release tiers defined with owners; every gate maps to a job.
- Workflow YAML parses; no secrets in files; quarantine process documented.

## Acceptance
- All checklist gates pass; pipeline run green on a trial branch.

## Validation Procedure
- `validate_skill` passes; `review_configuration` clean; checklist gates green;
  trial run evidence inspected.

## Common Failure Modes
- Floating toolchain breaks reproducibility → pin versions, hash container images.
- Long push builds get skipped → enforce the time budget by tiering, not by hoping.
- Artifact names collide across matrix axes → matrix values in every artifact name.

## Guardrails
- No secret values in workflow files, logs, or templates — names only.
- No destructive steps (force-push, delete) in generated pipelines.

## References
- CI provider workflow reference (public docs landing page).
- Project release policy and evidence expectations (project-local).
