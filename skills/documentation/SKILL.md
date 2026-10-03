# Documentation skill

Technical documentation engineers and auditors actually use: architecture
records, interface documents, user and service manuals, and the doc pipeline
that keeps them correct, versioned, and reviewed alongside code.

## 1. Purpose and scope

**Purpose.** Deliver documentation that is accurate at the release it
describes, traceable to the system it documents, and maintained with the same
discipline as code.

**In scope.** Document types (architecture, ICDs, API references, user/service
manuals, safety-manual appendices), docs-as-code pipeline, review and approval
workflows, versioning per release, and readability/accuracy standards.

**Non-goals.** Marketing content and in-code comments (see
`implementation` §3). Ends at a reviewed documentation set released with the
product.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 26511 Requirements for managers of information | 2018 | Documentation management across the life cycle | `https://www.iso.org/standard/70872.html` |
| 2 | ISO/IEC/IEEE 26514 Design and development of user documentation | 2022 | User-doc processes and quality criteria | `https://www.iso.org/standard/75888.html` |
| 3 | ISO 26262-10 Guidelines | 2018 | Documentation structure expectations for safety work products | `https://www.iso.org/standard/68392.html` |

## 3. Rules

1. **Docs as code.** Sources in version control, reviewed in the same
   merge-request flow as code, built by CI; generated artifacts (PDFs, sites)
   are reproducible from tagged sources. Wiki-only knowledge is tribal
   knowledge — migrate or lose it.
2. **Versioned with the product.** Each release ships its doc set; docs state
   the exact product version and baseline they describe. Stale version
   references are defects found by CI link/version checks, not by readers.
3. **Interfaces documented once.** APIs, protocols, and ICDs have a single
   normative source (generated from code/contracts where possible); duplicated
   interface descriptions in prose docs drift and are forbidden as normative.
4. **Safety-relevant docs reviewed.** Safety manuals, integration instructions,
   and assumptions-of-use documents follow the integrity level's independence
   rules (`safety` §6) — a safety manual reviewed only by its author is not
   evidence.
5. **Tested examples.** Code samples and procedures in docs are executed by CI
   (doctest-style or rig-run); untested examples rot and mislead.

## 4. Release gates (blocking)

1. Doc set built from the release tag; version references verified by CI.
2. Interface docs generated from normative sources, no prose duplicates.
3. Safety/assumption-of-use docs reviewed with required independence.
4. Examples and procedures executed green in CI.

## 5. Verification of this skill (Phase 4 gate)

- Standards carry number + version + clause + URL (§2).
