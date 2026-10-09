# Technology layer: DSP

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skills: `skills/edge-ai/` (fixed-point/deploy path), `skills/embedded-c/` (integer discipline)
- Platform overlay: `platforms/dsp/`
- Facets key: none yet — **gap**: no `dsp` platform in the facets vocabulary; engage via `--platform mcu` or `--platform soc` until extended
- Engage: `python -m axiom_cli engage --domain <domain>` (full slice, filter manually)
- Gates: fixed-point scaling proven, overflow analysis, cycle budget at worst-case corner
