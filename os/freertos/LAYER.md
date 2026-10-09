# OS layer: FreeRTOS

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/rtos/` (v1.2.0) — selection table, scheduling/IPC rules, MPU, WCET/timing verification
- Platform overlay: `platforms/freertos/`
- Facets key: `platforms: [rtos]` (FreeRTOS LTS kernel 11.3.0, MPU + MQTTv5 support to 2028-04-30)
- Engage: `python -m axiom_cli engage --platform rtos --domain <domain>`
- Gates: static allocation (`heap_4` justified or static), priority design reviewed, stack-overflow detection on
