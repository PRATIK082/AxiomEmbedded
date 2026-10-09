# OS layer: embedded-linux

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/embedded-linux/` (v1.2.0) — Yocto LTS policy, BSP structure, PREEMPT_RT, verified boot, OTA, hardening
- Platform overlay: `platforms/embedded-linux/`
- Facets key: `platforms: [linux]` (Yocto Wrynose 6.0 LTS for new designs, Scarthgap 5.0 maintenance)
- Engage: `python -m axiom_cli engage --platform linux --domain <domain>`
- Gates: layers pinned, SBOM + CVE scan, verified boot on hardware, OTA rollback tested
