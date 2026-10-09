# OS layer: NuttX

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skills: `skills/rtos/` (scheduling/timing), `skills/embedded-linux/` (POSIX userspace discipline)
- Platform overlay: `platforms/nuttx/`
- Facets key: `platforms: [rtos]` (closest match; NuttX POSIX API noted in the layer review)
- Engage: `python -m axiom_cli engage --platform rtos --domain <domain>`
- Gates: board config versioned, POSIX-surface dependencies listed, timing characterized
