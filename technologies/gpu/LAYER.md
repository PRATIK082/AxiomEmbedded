# Technology layer: GPU

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/edge-ai/` (v1.2.0) — delegate paths, latency/energy budgets
- Platform overlay: `platforms/gpu/`
- Facets key: none yet — **gap**: no `gpu` platform in the facets vocabulary; engage via `--platform soc` until extended
- Engage: `python -m axiom_cli engage --domain <domain>` (full slice, filter manually)
- Gates: op audit on the GPU path, p100 latency at worst-case corner, energy per inference
