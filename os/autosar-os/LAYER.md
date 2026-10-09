# OS layer: AUTOSAR OS

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/autosar/` (v1.2.0) — Classic layered rules, Adaptive ara/C++14, SOME/IP integration
- Platform overlay: `platforms/autosar-classic/` (Classic OS); `platforms/autosar-adaptive/` (Adaptive execution management)
- Facets key: `platforms: [autosar-classic]` / `[autosar-adaptive]`
- Engage: `python -m axiom_cli engage --platform autosar-classic --domain automotive`
- Gates: spec items by doc ID + release; human review required (safety-sensitive)
