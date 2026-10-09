# ADR-0006: Simple UI, Complex Automation (slice 1)

Date: 2026-10-03 | Status: accepted | Branch: `feature/simple-ui-ops`

## Context

Feature spec "Simple UI, Complex Automation": the user sees project status
and next action; YAML paths, branches, and matrix structures stay hidden.
User decisions (question round): stdlib HTML dashboard, fix/feature as plan
emitters, status measured from this repo's real data.

## Decision

- New single-implementation layer `packages/axiom_ops`: `get_status()`
  (real repo metrics: 47 skill versions, inventory counts, attention items),
  `plan_fix()` (10-step plan), `plan_feature()` (9-step plan).
- CLI: `axiom status [--format text|json]`, `axiom fix ID`, `axiom feature ID`.
- `axiom serve /` renders the single-screen HTML dashboard from the same
  `get_status()`; new `GET /v1/status`, `POST /v1/fix`, `POST /v1/feature`.
- SDK re-exports the three functions; MCP gains `get_status`, `plan_fix`,
  `plan_feature` tools — all interfaces stay in agreement.
- Zero new dependencies (stdlib + PyYAML, per ADR-0005).

## Consequences

- `axiom fix`/`feature` emit plans for harness execution; autonomous
  patching is explicitly out of scope for slice 1.
- Slice 2 candidates: `axiom init`/`discover`, user-project `.axiom` model,
  agreement tests for the new routes.
