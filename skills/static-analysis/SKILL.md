---
name: static-analysis
description: Checker layering, qualification, baselines, and triage for MISRA/CERT findings, incl. CodeQL Coding Standards packs run locally. Use when configuring analyzers or clearing violation backlogs.
version: 1.3.0
domains: [all]
platforms: [all]
axiom:
  dotted_name: axiom.legacy.static-analysis
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills:
  - axiom-static-analysis-triage
  checklists:
  - checklists/static-analysis-checklist.md
---

# Static-Analysis skill

Configuring, running, and dispositioning static analysis (SAST, MISRA/CERT
checkers, abstract interpretation, taint analysis) so findings become fixed
defects or documented deviations — never ignored warnings.

## 1. Purpose and scope

**Purpose.** Catch defect classes testing misses (undefined behavior, taint
flows, rule violations, concurrency hazards) as early and automatically as
possible, with a zero-new-findings bar on every change.

**In scope.** Tool selection and qualification, checker configuration
(rulesets, baselines), CI integration, finding triage and disposition,
deviation records, metrics (density, fix rate, escape rate), and abstract
interpretation for safety-critical proof goals.

**Non-goals.** Dynamic testing (see `unit-test`, `system-test`) and manual
review technique (see `code-review`). Ends at a clean, evidenced analysis
record per change and per release.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | MISRA C | MISRA C:2025 (March 2025, current) | Enforceable subset for static checking | `https://misra.org.uk/` |
| 2 | CERT C | Current | Taint, API-misuse, and secure-coding checkers | `https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard` |
| 3 | ISO 26262-6 Software level | 2018 | Clause 9 verification: static analysis highly recommended ≥ ASIL B, required methods at C/D | `https://www.iso.org/standard/68389.html` |
| 4 | CWE Top 25 / CVE linkage | Annual (MITRE) | Weakness taxonomy for finding classification and training feedback | `https://cwe.mitre.org/top25/` |
| 5 | CodeQL Coding Standards (query packs, MIT) | Pinned release (CLI per upstream `supported_codeql_configs.json`) | Reused pristine: MISRA C/C++, AUTOSAR C++14, CERT C/C++ queries; SARIF 2.1.0; ISO 26262 qualification valid only as distributed | `https://github.com/github/codeql-coding-standards` |

## 3. Toolchain rules

1. **Layered checkers.** Compiler warnings (`-Wall -Wextra -Werror`, gcc +
   clang) → MISRA/CERT checker → deep analyzer (abstract interpretation /
   taint) for safety-critical paths. Each layer's scope is documented; gaps
   between layers are known, not assumed covered.
2. **Qualified for the claim.** At ASIL C/D, analysis tools are qualified per
   `safety` §6 (TCL/ASCL); the tool version, ruleset version, and
   configuration are release evidence.
3. **Baseline honestly.** Legacy code gets a dated baseline of pre-existing
   findings with burn-down; new/changed code is zero-tolerance from day one.
   Baselines shrink monotonically — growth blocks the release.
4. **Reuse the CodeQL packs, never redevelop or fork them.** The MISRA/CERT
   checker layer is `tools/codeql-standards-bridge/` running upstream packs
   (`misra-c`, `cert-c`, `misra-cpp`, `cert-cpp`, `autosar-cpp`) locally via
   a pinned CodeQL CLI; suites `default` (violations), `audit` (review
   candidates), `strict` (deliberate-looking). Forking or editing queries
   voids their ISO 26262 tool qualification — deviations go in
   `coding-standards.yml` (rule ID + justification + scope), never in query
   edits. SARIF 2.1.0 + `findings.json` + `provenance.json` are the evidence.

## 4. Triage and disposition

Every finding ends in exactly one state: fixed, deviation (rule ID +
rationale + impact review + approver + expiry per `implementation` §4), or
false-positive with checker-version-specific justification (re-validated on
tool upgrade). Triage SLAs scale with severity and integrity level; security
taint findings follow `security` disclosure timelines. Suppression without a
deviation ID is a defect.

## 5. Release gates (blocking)

1. Zero new findings on changed code; baseline burn-down on plan or better.
2. Every open finding dispositioned (fixed/deviation/false-positive with evidence).
3. Tool + ruleset versions recorded; qualification evidence current for the ASIL.
4. Escape review: field/test-escaped defects feed back into ruleset tuning.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL (§2).
- No unverified-clean claims: configuration and version always attached.
