# OS layer: Zephyr

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/rtos/` (v1.2.0) — scheduling, IPC, MPU, timing verification
- Platform overlay: `platforms/zephyr/`
- Facets key: `platforms: [rtos]` (Zephyr LTS, 1000+ boards, POSIX/tickless)
- Engage: `python -m axiom_cli engage --platform rtos --domain <domain>`
- Gates: devicetree-driven config versioned, west manifest pinned, thread-budget analysis
