# ADR-0003: autosar as template replication 2

Status: accepted
Date: 2026-10-03
Scope: embedded-skills-deep-update v1.0.0, Phase 3

## Context

`mcu` template accepted (ADR-0001), `rtos` replicated (ADR-0002). `autosar` is
next: Classic/Adaptive development is safety-relevant (ISO 26262-6).

## Decision

Replicate the template with AUTOSAR-specific content pinned to Phase 2
research: Classic R24-11 baseline (R25-11 noted current, verify-before-cite),
Adaptive R24-11, Foundation R24-11 safety requirements (Doc ID 986), Adaptive
C++14 API [RS_AP_00114], SOME/IP Foundation R22-11 (Doc ID 696). SOME/IP daemon
pattern for Classic↔Adaptive integration. MISRA C:2025 for Classic,
MISRA C++:2023 (stricter-wins) for Adaptive.

## Consequences

- Positive: platform choice becomes an evidenced decision; spec items cited by
  document ID + release.
- Negative: R25-11 deltas and CAPI implementation assets need a follow-up pass.
- Follow-up: human review mandatory before the `autosar` PR (safety-relevant).
