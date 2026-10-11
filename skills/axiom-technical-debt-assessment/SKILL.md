---
name: axiom-technical-debt-assessment
title: Technical Debt Assessment
description: >
  Inventories technical debt as a scored register (principal, interest, contagion,
  paydown cost), prioritizes paydown with explicit trade-offs, and produces a
  reviewable paydown plan tied to releases.
version: 0.1.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.cross-domain.technical.debt.assessment
  domain: cross-domain
  subdomain: review
  category: review
  maturity: experimental
  owner: axiom-embedded
  tags: [tech-debt, quality, planning, review]
  related_skills: [axiom-architecture-decision-records, axiom-platform-architecture-review, axiom-static-analysis-triage]
  lifecycle: [design, implementation, integration, release, operations]
  standards: []
  artifact_types: [debt register, paydown plan]
  mcp_tools: [run_skill, validate_skill, generate_report, generate_checklist]
  risk_level: low
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill, generate_report]
---

# Axiom Technical Debt Assessment

## Purpose
Replace vibes ("the codebase is a mess") with a register: each debt item names its
location, kind, principal (cost already paid in workarounds), interest rate (cost per
release if left), contagion (what else it infects), and paydown cost — then ranks
paydown by return so planning decisions are explicit and reviewable.

## When to Use
- Planning needs a defensible paydown slice, or debt keeps losing to features silently.
- Handover, audit, or platform review asks "where is the risk in this codebase".
- Recurring defects cluster in one area and workarounds are accumulating.

## When Not to Use
- As a blame instrument; the register records items, owners, and plans — never fault.
- When nothing will be funded; an unplanned register rots — timebox the assessment.

## Required Inputs
- Repository path and scope (whole tree or named subsystems).
- Objective: full inventory, targeted area, or paydown plan for a release.
- Constraints: paydown budget (e.g. percent of capacity), risk appetite.

## Optional Inputs
- Defect history, triage logs, prior ADRs, prior run manifests.

## Prerequisites
- `axiom doctor --skip-tests` green; static-analysis triage current for the scope.

## Execution Workflow
1. Normalize scope, budget, and appetite; timebox the inventory pass.
2. Inventory debt from code, tests, docs, and interviews: duplication, obsolete
   branches, missing tests, fragile builds, undocumented assumptions, deferred
   decisions — one row each in `templates/debt-register.template.csv`.
3. Score each row: principal (S/M/L + note), interest per release, contagion count,
   paydown cost; safety/security-adjacent items flagged for human review.
4. Rank by interest-per-cost; cut the paydown slice at the budget line; everything
   above the line gets an owner and a target release, everything below stays listed.
5. Convert paydown items into tracked work with acceptance notes; link ADRs where
   the debt stems from a recorded decision.
6. Dry-run the register + plan review; apply; re-run `validate_skill`.

## Tool Invocations
- `run_skill` with structured context; dry-run before publishing the register.
- `generate_report` for the paydown-plan summary.
- `validate_skill` must pass before the plan is committed to a release.

## Decision Rules
- Debt touching safety/security paths outranks pure-velocity debt regardless of score.
- No paydown item without an owner and a target release; ownerless plans are wishes.
- Estimates are ranges, never false precision; re-score quarterly or per release.
- Retire rows with evidence (the fix + test), never by editing the register silently.

## Workflow
Follow Execution Workflow; record scoring rationale and budget-line placement in the
run manifest.

## Deliverables
- Debt register CSV plus ranked paydown plan under the agreed output directory.
- Run report + manifest under `.axiom/runs/<timestamp>/axiom-technical-debt-assessment/`.

## Acceptance Criteria
- Every row scored on all four axes; budget line drawn; owners + releases assigned
  above the line; safety/security flags reviewed by a human.

## Acceptance
- All checklist gates pass; plan accepted by the owning team.

## Validation Procedure
- `validate_skill` passes; register schema check; checklist gates green; sample
  audit of 10% of rows against code.

## Common Failure Modes
- Register becomes write-only → paydown slice per release or stop assessing.
- Interest guessed, never observed → tie each interest claim to a defect or delay.
- Debt used in performance conversations → guardrail violation; reset framing.

## Guardrails
- No personal attributions of fault; no secrets in the register; no network calls.

## References
- Prior ADRs and triage logs (project-local).
- Release plan the paydown slice targets (project-local).
