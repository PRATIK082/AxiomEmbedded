---
name: axiom-deployment-readiness
title: Deployment readiness
description: >
  Evaluates whether release artifacts are deployment-ready across pip, npm,
  GitHub Release, and MCP registry channels with version parity and rollback
  plans. Use when a deployment-readiness review or publish decision is requested.
version: 1.2.0
author: PRATIK082
license: Apache-2.0
domains: [generic-embedded]
platforms: [mcu]
axiom:
  dotted_name: axiom.generic-embedded.deployment.readiness
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

# Axiom Deployment readiness

## Purpose
Decide, with evidence, whether a release artifact set is deployment-ready on
each publish channel. Requires production-readiness PASS first; then verifies
per-channel packaging, installability, version parity, and rollback planning.

## When to Use
- A publish decision is requested (PyPI, npm, GitHub Release, MCP registry).
- A release tag candidate needs per-channel verification before push.
- Post-release verification of install paths (`pip install`, `npm i -g`, `axiom install`).

## When Not to Use
- Before production-readiness gates pass (run `axiom-production-readiness` first).
- As certification proof or a substitute for qualified safety/security review.

## Required Inputs
- Repository path and release tag or branch under review.
- Target channels (pip, npm, github-release, mcp-registry).
- Version under test (must equal VERSION file).

## Optional Inputs
- TestPyPI / dry-run publish credentials or tokens.
- Prior deployment reports for regression comparison.

## Prerequisites
- Production-readiness verdict READY (or READY WITH WAIVERS covering only non-packaging items).
- Clean working tree; tag points at the verified commit.

## Execution Workflow
1. Confirm production-readiness PASS and record its report reference.
2. Verify version parity across all carriers (see rule below).
3. Run per-channel checks in order; record evidence for each.
4. Verify install smoke tests from a clean environment per channel.
5. Confirm rollback plan exists for every channel being published.
6. Write the deployment report and run manifest under `.axiom/runs/`.

## Version Parity Rule
`VERSION` file == `pyproject.toml` version == `package.json` version ==
`axiom --version` output. Any drift BLOCKS deployment on all channels.

## Per-Channel Checks
| Channel | Checks |
|---------|--------|
| pip (PyPI) | `python -m build` succeeds; `twine check dist/*` clean; sdist contains skills/agents/registries/schemas/profiles/workflows/domains/platforms/configs/clients/docs per MANIFEST.in; wheel installs; `axiom --version` matches; bare-wheel honesty: wheel alone is MCP-server-only, full content needs `--source`. TestPyPI upload first for new channels. |
| npm | `package.json` version parity; `npm pack --dry-run` lists bin shim + README + LICENSE; bin shim resolves `axiom` on PATH or falls back to `python -m axiom_cli`; install smoke on clean machine documents the pip dependency. |
| GitHub Release | Tag `v*` format; `release.yml` workflow green (build, publish, release notes); CHANGELOG semver entry present; no uncommitted gate-relevant changes at tag. |
| MCP registry | `.mcp.json` current; `clients/mcp.json` has no absolute cwd; registry PR follows upstream template; server entry starts (`axiom mcp`). |
| Client mirrors | `sync_clients` derived files current (`skill_pipeline --check` covers STALE); `axiom install --client <each>` smoke per test_install matrix. |

## Decision Rules
- Per-channel verdicts: READY, NOT READY, WAIVED (waiver + approval recorded).
- Overall READY requires every targeted channel READY; one NOT READY blocks publish on that channel only if channels are independent, otherwise blocks all.
- Never publish secrets: tokens via environment or store, never in files.
- Pushing, tagging, and publishing are user-handled approval gates; the skill reports readiness, it does not publish.

## Tool Invocations
- Deterministic CLI/packaging checks first; model judgment only for waiver rationale review.

## Deliverables
- Deployment report (per-channel results, install smoke logs, parity proof, rollback plan refs) + run manifest under `.axiom/runs/<timestamp>/axiom-deployment-readiness/`.

## Acceptance Criteria
- Parity proof attached; every targeted channel has a recorded result.
- Rollback plan referenced for every channel marked READY.

## Acceptance
- Reviewer reproduces parity and at least one clean-environment install per READY channel.

## Validation Procedure
- validate_skills + checklist + human gate for publish approval.

## Common Failure Modes
- Version drift between carriers -> BLOCKED on all channels until aligned.
- STALE derived client mirrors -> regenerate via `axiom skills apply`, re-run.
- Bare-wheel install expected to carry skills -> document `--source` requirement instead.
- Absolute cwd baked into `clients/mcp.json` -> fails portability check; fix at install time.
- Publishing attempted before production gates pass -> stop; run production-readiness first.

## Guardrails
- No secrets/shell/net beyond packaging CLIs; never claim compliance.






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.





## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | (none declared) | LOW |


## Impact tiers

| Tier | Meaning |
|---|---|
| CRITICAL | Safety/security-critical; requires human approval and impact assessment |
| HIGH | Significant impact; requires review |
| MEDIUM | Moderate impact; standard review |
| LOW | Minor impact; routine review |

### Rule impact assignments

All rules in this skill default to MEDIUM unless marked CRITICAL or HIGH
in the rule ID -> clause map above.

## Deviation management

Any deviation must be recorded with: Rule ID, reason, file/location,
approver, and date. CRITICAL-rule deviations require safety-lead approval
and an impact assessment. Deviations are first-class artifacts, not comments.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## References
- Standard identifiers + landing URLs only.
