# Evidence skill

Assembling audit-ready evidence: what counts as evidence, how it is captured,
stored, versioned, and presented for safety/security assessment and release
sign-off.

## 1. Purpose and scope

**Purpose.** Make every claim verifiable by an independent party months later —
no evidence, no claim, no release.

**In scope.** Evidence taxonomy (reviews, analyses, test reports, tool outputs,
approvals), capture automation, storage and retention, the repo's evidence
schema (`schemas/evidence.schema.json`, `compliance-evidence.schema.json`),
and evidence review before assessment.

**Non-goals.** Creating the engineering artifacts themselves (owned by each
lifecycle skill). This skill governs their packaging and integrity.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-8 | 2018 | Clause 10 documentation: work-product identification, versioning, approval records | `https://www.iso.org/standard/68390.html` |
| 2 | DO-178C | 2011 | §11 software life-cycle data: plans, standards, verification results, configuration index | `https://www.rtca.org/products/software-considerations-in-airborne-systems-and-equipment-certification-do-178/` |
| 3 | ISO/IEC/IEEE 15289 | 2019 | Content of life-cycle information items (reviews, reports, plans) | `https://www.iso.org/standard/73196.html` |

## 3. Evidence taxonomy

| Class | Examples | Captured by |
|-------|----------|-------------|
| Review records | Requirement/architecture/code review minutes with dispositions | Human sign-off + tool export |
| Analysis results | FMEDA, FTA, WCET, timing, static-analysis reports | Tool output, version-pinned tool |
| Test results | Unit/integration/system/validation reports with environment | CI artifacts + hardware records |
| Tool qualification | TCL/TQL reports, validation suites | `safety` §6 / DO-330 process |
| Approvals | Baselines, waivers, deviation approvals, assessment reports | Named approver + date, never anonymous |

## 4. Integrity rules

1. **Tool outputs are primary.** Hand-written summaries support but never
   replace the tool artifact (coverage XML, test logs, analyzer reports).
   Record tool name + version with every artifact.
2. **Immutable once approved.** Approved evidence is read-only; superseding
   requires a new version with a change reason — silent edits to evidence are a
   process violation.
3. **Retention planned.** Retention periods defined per artifact class at
   project start (product lifetime + regulatory tail, typically 10–15 years
   automotive); storage format must remain readable (PDF/A or plain-text
   formats, no proprietary-only binaries).
4. **Schema-conformant.** Machine-readable evidence validates against
   `schemas/evidence.schema.json` and `compliance-evidence.schema.json`;
   non-validating evidence is incomplete work.

## 5. Release gates (blocking)

1. Evidence checklist complete per the integrity level (no missing classes).
2. All artifacts schema-valid with tool versions recorded.
3. Approvals named and dated; no self-approval of safety/security artifacts.
4. Retention locations assigned and verified readable.

## 6. Verification of this skill (Phase 4 gate)

- Spot-check: pick any claim, retrieve its evidence in under 5 minutes.
- Schema validation enforced in CI where evidence is machine-readable.
