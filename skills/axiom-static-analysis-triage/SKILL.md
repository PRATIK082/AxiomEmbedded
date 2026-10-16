---
name: axiom-static-analysis-triage
title: Static Analysis Triage
description: >
  Triages static-analysis findings (MISRA, CERT, generic checkers) with a
  deterministic classifier script: buckets severity, tracks baselines and waivers,
  and produces a reviewable triage log with gate verdicts.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.cross-domain.static.analysis.triage
  domain: cross-domain
  subdomain: verification
  category: verification
  maturity: experimental
  owner: axiom-embedded
  tags: [static-analysis, misra, triage, quality]
  related_skills: [axiom-platform-architecture-review, axiom-test-automation]
  lifecycle: [implementation, integration, verification, release]
  standards: [MISRA C, CERT C]
  artifact_types: [triage log, baseline, gate verdict]
  mcp_tools: [run_skill, validate_skill, generate_report, generate_checklist]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill, generate_report]
---

# Axiom Static Analysis Triage

## Purpose
Turn a raw static-analysis dump into a dispositioned triage log: each finding is
classified (fix, waive with rationale, false positive with evidence, deferred with
expiry), new findings versus the committed baseline are isolated, and a release gate
verdict is produced. Ships a deterministic classifier script so re-runs are identical.

## When to Use
- A checker run (MISRA, CERT C, compiler warnings-as-findings, custom rules) needs
  review before merge or release.
- Finding counts must trend down across releases with a committed baseline.
- Waivers need expiry and ownership instead of living forever in comments.

## When Not to Use
- As proof of absence of defects or of standards compliance; triage organizes
  findings, it does not certify code.
- When the checker configuration itself is unreviewed — pin tool version and rule
  set first.

## Required Inputs
- Repository path and the findings export (CSV picklist: file, line, rule id,
  severity, message) or the checker invocation to reproduce it.
- Objective: gate level (advisory, merge-blocking, release-blocking).
- Constraints: rule set, baseline file path, waiver policy.

## Optional Inputs
- Prior triage logs and baselines for trend comparison.

## Prerequisites
- `axiom doctor --skip-tests` green; checker output reproducible from a clean tree.

## Execution Workflow
1. Normalize the request: rule set, gate level, baseline path, waiver policy.
2. Reproduce or ingest the findings export; verify file/line references resolve.
3. Run `scripts/classify_findings.py` to bucket findings by severity class and to
   diff against the baseline (new / fixed / carried).
4. Disposition every new finding: fix, waive (rationale + owner + expiry), false
   positive (evidence), or deferred (expiry + tracking id). No silent carries.
5. Expire stale waivers: any waiver past expiry without renewal becomes a finding.
6. Emit the triage log (`templates/triage-log.template.csv`) and the gate verdict.
7. Dry-run the report; apply; re-run `validate_skill`.

## Tool Invocations
- `run_skill` with structured context; dry-run before writing baselines.
- `generate_report` for the gate-verdict summary.
- `validate_skill` must pass before a release-blocking verdict is honored.

## Decision Rules
- Safety-related rule violations are never waived without a dated human sign-off
  naming the compensating control.
- A waiver always has owner + expiry; ownerless or evergreen waivers are findings.
- Baseline may only shrink by fixes, never by reclassification; reclassification
  requires evidence in the log.
- If new-findings count exceeds the agreed threshold, verdict is FAIL regardless
  of severity mix.

## Workflow
Follow Execution Workflow; record checker version, rule set hash, and per-finding
dispositions in the run manifest.

## Deliverables
- Triage log CSV and updated baseline under the agreed output directory.
- Gate verdict (PASS/FAIL with counts per bucket).
- Run report + manifest under `.axiom/runs/<timestamp>/axiom-static-analysis-triage/`.

## Acceptance Criteria
- 100% of new findings dispositioned; zero ownerless waivers; baseline diff clean.
- Classifier script re-run reproduces the log byte-for-byte on identical input.

## Acceptance
- All checklist gates pass; safety-related waivers carry human sign-off.

## Validation Procedure
- `validate_skill` passes; classifier unit tests pass; checklist gates green;
  spot-check 10% of false-positive claims against code.

## Common Failure Modes
- Checker version drift between runs → pin version + rule set; record both in manifest.
- Suppression comments without expiry → convert to log waivers or flag as findings.
- Baseline committed with generated code included → scope baseline to owned sources.

## Guardrails
- No secrets in logs; findings excerpts stay within the repo; no network calls.
- Never claim MISRA/CERT compliance from triage output.

## References
- MISRA C and CERT C rule identities (public rule designations only, no quoted text).
- Checker user manual for the pinned tool version (project-local).
