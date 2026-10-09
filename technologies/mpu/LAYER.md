# Technology layer: MPU

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/mpu/` (v1.2.0) — selection from measured load, ECC/DDR, power sequencing, debug-by-design
- Platform overlay: `platforms/mpu/`
- Facets key: `platforms: [mpu]`
- Engage: `python -m axiom_cli engage --platform mpu --domain <domain>`
- Gates: DDR high-speed discipline, Handoff gates, maintenance per LTS policy
