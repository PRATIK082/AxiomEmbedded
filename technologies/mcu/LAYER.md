# Technology layer: MCU

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/mcu/` (v1.2.0) — core selection, MPU/TrustZone, startup/linker, HAL, CMake, RTOS choice
- Platform overlay: `platforms/mcu/`
- Facets key: `platforms: [mcu]`
- Engage: `python -m axiom_cli engage --platform mcu --domain <domain>`
- Gates: coverage per ASIL (`configs/skill-update.yaml`), zero-warnings build, traceability gap-free
