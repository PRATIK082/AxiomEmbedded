# Artifact contract guide

Canonical format is YAML validated against `schemas/assurance-*.schema.json`.

## Envelope (all artifacts)

artifact_id, schema_version, kind, status, domain, standards, created_at,
updated_at, author, reviewer, assumptions, evidence, traceability,
open_questions, approval_status.

## Kinds

| kind | schema | body |
|---|---|---|
| system-scope | assurance-scope | system, operating_context, boundaries |
| hazard-risk | assurance-hazard-risk | hazards[] (HAZ-xxx, severity, controls/rationale) |
| safety-requirements | assurance-safety-requirements | requirements[] (REQ-xxx, covers_hazards, verification) |
| vnv-plan | assurance-vnv-plan | test_cases[] (TEST-xxx), trace_matrix[] |
| threat-model | assurance-threat-model | threats[] (SEC-xxx, severity, controls) |
| review-report | assurance-review | target_artifact, verdict, findings[] (REV-xxx) |

## Rules

- UTC ISO 8601 timestamps; stable IDs; no duplicate IDs per artifact.
- Unknowns are UNKNOWN or OPEN with an owner; never invented.
- Test results default to not-run; pass requires EVD-xxx evidence.
- Reviewer verdicts: accept, accept-with-actions, revise-and-resubmit
  (mandatory with any Blocker).
