# Validation campaign: {{objective}}

Target: {{target}} ({{target_kind}})
Engine: {{engine}} (layer: {{layer}})

## Pre-check

- [ ] Bench reachable (instruments ping)
- [ ] DUT power rails nominal
- [ ] Firmware binary hash matches {{expected_hash}}

## Execution

{{steps}}

## Triage

- Diagnostic bundle: {{bundle_ref}}
- Classification: Bench issue | Hardware fault | Firmware regression

Evidence: run-manifest.json
