# axiom-sil-hil-bridge: overview

Promotes SIL cases to HIL hardware without rewriting assertions. Same logic,
widened timing tolerances, dual verdicts.

## Promotion flow

1. Freeze SIL baseline (simulator plus model revision plus verdicts).
2. Apply tolerance policy (per-assertion HIL widening with physical rationale).
3. Generate HIL suite (logical bench names only).
4. Pre-check, flash attested image, execute on hardware.
5. Promotion report: per-case SIL status, HIL status, tolerance delta.

## Iron rule

A SIL pass is never hardware proof. HIL failures are findings, never waived
by SIL passes.
