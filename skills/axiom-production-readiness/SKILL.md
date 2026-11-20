---
name: axiom-production-readiness
title: Production readiness
description: >
  Evaluates whether an AxiomEmbedded change or release branch is production-ready
  by running the machine-gated checklist (pipeline, tests, validation, evidence,
  approvals). Use when a production-readiness review or release gate decision is requested.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [generic-embedded]
platforms: [mcu]
axiom:
  dotted_name: axiom.generic-embedded.production.readiness
  domain: generic-embedded
  maturity: experimental
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  risk_level: medium
  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []
  related_skills: []
---

# Axiom Production readiness

## Purpose
Decide, with evidence, whether a change or release branch is production-ready.
Production-ready means every machine gate is green, evidence is recorded, and
required human approvals are obtained. A missing result is never a PASS.

## When to Use
- A release gate decision is requested for a branch, PR, or tag.
- A change claims to be complete and needs an independent readiness verdict.
- Nightly drift or pre-release review needs a repeatable gate checklist.

## When Not to Use
- As certification proof (ASPICE, ISO 26262, IEC 61508 are separate assessments).
- As a substitute for domain safety/security qualified review.

## Required Inputs
- Repository path and branch or tag under review.
- Scope of the change (skill IDs, files, or release notes).
- Risk level and whether safety/security-critical content is touched.

## Optional Inputs
- Prior readiness reports for trend comparison.
- Waiver requests with justification and approver.

## Prerequisites
- Derived files regenerated (`axiom skills apply`) so checks run on current content.
- Clean working tree for release verdicts (no uncommitted gate-relevant changes).

## Execution Workflow
1. Normalize request: record scope, risk, and approver requirements.
2. Run machine gates in order; stop at the first blocking FAIL (record, do not skip).
3. Collect evidence artifacts for every gate (logs, reports, manifests).
4. Evaluate waivers: each WAIVED gate needs written justification plus approval.
5. Write the readiness report and run manifest under `.axiom/runs/`.
6. Summarize verdict: READY, READY WITH WAIVERS, or NOT READY with blockers.

## Production Gates
| # | Gate | Command | Required result |
|---|------|---------|-----------------|
| G1 | Skill pipeline | `python scripts/skill_pipeline.py --check` | OK (270+ skills, no STALE) |
| G2 | Unit tests | `python -m pytest -q` | all pass |
| G3 | Doctor | `python -m axiom_cli doctor --skip-tests` | repo PASS, exit 0 |
| G4 | Repo validation | `python -m axiom_cli repo validate` | PASS |
| G5 | Compile hygiene | `python -m compileall -q axiom_cli packages scripts` | clean |
| G6 | Install smoke | `axiom install --client opencode --path <tmp>` | status ok, idempotent re-run |
| G7 | Wheel build | `python -m pip wheel . --no-deps -w <tmp>` | builds; MANIFEST grafts content trees |
| G8 | Secrets scan | repo secret/vuln scan | no committed secrets |
| G9 | Version parity | VERSION == pyproject == `axiom --version` | all equal |
| G10 | Docs currency | README skill count, CHANGELOG semver entry | current |

## Decision Rules
- Gate states: PASS, FAIL, BLOCKED, NOT RUN, WAIVED. A missing result is NOT RUN, never PASS.
- Any blocking FAIL without an approved waiver yields NOT READY.
- WAIVED requires written justification and an explicit human approval; record both.
- `safety_critical: true` or `risk_level: high` content requires human sign-off before READY.
- Never claim certification, compliance, or ASIL/DAL/SIL attainment from these gates.

## Tool Invocations
- run_skill dry-run first; validate_skill gates release.
- Prefer deterministic CLI checks over model judgment for every gate above.

## Deliverables
- Readiness report (verdict, per-gate results, waivers, blockers) + run manifest under `.axiom/runs/<timestamp>/axiom-production-readiness/`.

## Acceptance Criteria
- Every gate has a recorded result with evidence attached.
- Verdict follows the decision rules with no invented results.

## Acceptance
- Same gates, machine-checkable; reviewer reproduces G1-G9 independently.

## Validation Procedure
- validate_skills + checklist + human gate for WAIVED items.

## Common Failure Modes
- Gate skipped to save time -> mark NOT RUN; verdict cannot be READY.
- Red gate waived without approval -> invalid waiver; verdict NOT READY.
- Stale derived files (pipeline reports STALE) -> regenerate and re-run.
- Version drift between VERSION, pyproject, CLI -> BLOCKED until aligned.

## Guardrails
- No secrets/shell/net; never claim compliance.


## Deviation management

Any deviation from a rule or standard must be recorded with: Rule ID, reason,
file/location, approver, and date. Deviations are tracked as first-class
artifacts, not comments. (Straion pattern.)


## Builder + reviewer

This skill follows the builder + reviewer pattern: the builder produces the
artifact, the reviewer independently verifies it before acceptance. No
artifact is accepted without reviewer sign-off.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## Copyright-safe standards

Never reproduce normative standards text. Store identifiers, clause numbers,
applicability metadata, mappings, and project-authored interpretations only.


## References
- Standard identifiers + landing URLs only.
