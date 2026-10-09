# Technology layer: NPU

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/edge-ai/` (v1.2.0) — quantization pipeline, delegate op audit, arena budgeting
- Platform overlay: `platforms/npu/`
- Facets key: none yet — **gap**: no `npu` platform in the facets vocabulary; engage via `--platform soc` until extended
- Engage: `python -m axiom_cli engage --domain <domain>` (full slice, filter manually)
- Gates: quantization spec of the NPU toolchain is binding; on-device accuracy delta recorded
