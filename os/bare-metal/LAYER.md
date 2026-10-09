# OS layer: bare-metal

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/bare-metal/` (v1.2.0) — reset path, init order, fault handlers, ISR discipline, super-loop/time-triggered, sleep accounting
- Platform overlay: `platforms/bare-metal/`
- Facets key: `platforms: [bare-metal]`
- Engage: `python -m axiom_cli engage --platform bare-metal --domain <domain>`
- Gates: no hidden allocation, WCET-bounded ISRs, linker-map memory proof
