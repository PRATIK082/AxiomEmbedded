# Technology layer: SoC

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/soc/` (v1.2.0) — heterogeneous A/R/NPU allocation, inter-core protocols, safety-island isolation, PSCI/SCMI, power/thermal
- Platform overlay: `platforms/soc/`
- Facets key: `platforms: [soc]`
- Engage: `python -m axiom_cli engage --platform soc --domain <domain>`
- Gates: cross-die safety partitioning, secure boot chain, thermal analysis evidence
