---
name: configuration-management
description: Version-everything, immutable baselines, and CI identification. Use when setting up version control, baselines, or audits.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Configuration-Management skill

Version control, baselines, branching, and configuration identification for
embedded products — so any shipped binary maps to an exact, reproducible
source configuration.

## 1. Purpose and scope

**Purpose.** Guarantee that every artifact (code, config, toolchains, docs) is
identified, versioned, and retrievable, and that baselines are immutable points
the project can build, test, and ship from.

**In scope.** Repository structure (mono vs multi-repo with manifest pinning),
branching strategy, baseline and tag discipline, configuration identification
(CIs), status accounting, and configuration audits.

**Non-goals.** Day-to-day editing workflows and release ceremonies (see
`release`). Ends at an auditable configuration system.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 10007 Configuration management | 2017 | Identification, control, status accounting, audit | `https://www.iso.org/standard/70400.html` |
| 2 | EIA-649 Configuration Management | Rev C (2019) | Principles, CIs, change control, audits | `https://www.sae.org/standards/content/eia649c/` |
| 3 | ISO 26262-8 Supporting processes | 2018 | Clause 10 documentation; change/configuration management for safety | `https://www.iso.org/standard/68390.html` |

## 3. Rules

1. **Everything versioned.** Source, build scripts, toolchain files, configs,
   device trees, test data, and docs live in version control. Binary blobs
   (vendor SDKs, toolchains) are versioned by reference: URL + hash + license
   recorded, never an unexplained zip.
2. **Baselines immutable.** Release baselines are tags on exact revisions
   including submodule/manifest pins; history after a baseline never rewrites
   it. Rebuild-from-tag is demonstrated, not assumed (see `build-system` §4).
3. **Branching with purpose.** `main` always builds and passes host tests;
   feature branches short-lived; release branches frozen except for
   safety/security fixes with impact analysis (see `change-impact`).
4. **Configuration identification.** Each CI (firmware image, BSP, calibration
   set, compliance pack) has an ID, version, and status; the shipped product's
   CI list is part of the release record (see `release`) and the safety case
   where applicable (`safety` §7).
5. **Status accounting.** Dashboards answer at any time: what changed since
   baseline X, which change requests are open, which CIs are affected. Audits
   (functional + physical configuration audits) run per release.

## 4. Release gates (blocking)

1. Baseline tag complete with pins; rebuild-from-tag demonstrated.
2. CI list accurate; no untracked blobs in the shipped configuration.
3. Configuration audit findings closed or waived with expiry.

## 5. Verification of this skill (Phase 4 gate)

- Standards carry number + version + clause + URL (§2).
