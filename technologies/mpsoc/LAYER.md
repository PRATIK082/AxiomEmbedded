# Technology layer: MPSoC

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/mpsoc/` (v1.2.0) — NoC QoS budgeting, coherency domains, PL-as-hardware timing closure
- Platform overlay: `platforms/mpsoc/`
- Facets key: `platforms: [mpsoc]`
- Engage: `python -m axiom_cli engage --platform mpsoc --domain <domain>`
- Gates: NoC bandwidth proof, cross-die partitioning, secure boot across dies
