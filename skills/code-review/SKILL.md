---
name: code-review
description: Peer-review practice with checklists, size limits, and independence rules. Use when reviewing changes or setting up review policy.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Code-Review skill

Human peer review that finds what automation cannot: wrong requirements,
missing error paths, concurrency hazards, untestable structure, and
architecture drift — with a lightweight process engineers actually follow.

## 1. Purpose and scope

**Purpose.** Every merged change is read and understood by at least one
qualified engineer besides its author, with findings tracked to disposition.

**In scope.** Review scope rules, reviewer qualification and independence,
checklists per change class, finding severity and SLAs, review metrics, and
the interface to static analysis (`static-analysis`) and testing (`unit-test`).

**Non-goals.** Style policing (automate formatting; never spend review cycles
on it) and management approval theater. Ends at a merged-or-rejected change
with recorded rationale.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | IEEE 1028 Peer reviews | 2008 (reaffirmed) | Inspection roles, entry/exit criteria, data collection | `https://standards.ieee.org/standard/1028-2008.html` |
| 2 | ISO 26262-6 Software level | 2018 | Clause 6 design/code verification with independence per ASIL | `https://www.iso.org/standard/68389.html` |
| 3 | Google engineering-practices review guidance | Current (industry practice, non-normative) | Reviewer responsiveness, finding severity, small-change discipline | `https://google.github.io/eng-practices/review/` |

## 3. Process rules

1. **Automate first.** Formatting, static analysis, and unit tests pass before
   human review starts; reviewers never check what CI can check.
2. **Small changes.** Reviews cover ≤400 changed lines; larger changes are
   split or reviewed in stacked parts with an architecture overview attached.
3. **Checklist per class.** Driver changes check register/errata/timeouts
   (`drivers`); safety changes check traceability and independence (`safety`);
   concurrency changes check ownership and race freedom (`rtos`,
   `implementation` §3.4). Generic "LGTM" on a checklist-gated change is a
   process violation.
4. **Independence scales with integrity.** ASIL C/D and DAL A/B changes require
   a reviewer independent of the author (different person, no shared
   authorship); safety assessments are never self-reviewed.
5. **Findings tracked.** Every comment is a finding with severity
   (blocking/major/minor) and disposition (fixed/won't-fix with rationale);
   blocking findings gate the merge, period.

## 4. Anti-patterns (blocking review findings)

Drive-by approval without comments on non-trivial changes, style-only reviews
that miss logic defects, author-shopping for lenient reviewers, and post-merge
"reviews" on safety-relevant code.

## 5. Release gates (blocking)

1. Every merged change reviewed with dispositions recorded.
2. Independence requirements met per integrity level.
3. Review metrics healthy (coverage of changes, finding density, turnaround)
   with trends reviewed each increment.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL (§2).
- Review records are evidence per `evidence` taxonomy.
