# Technology layer: FPGA

Pointer layer per `Feature.md`. Canonical content lives in the platform
overlay — this file only links it. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skills: `skills/hardware-architecture/` (budgets, HSI), `skills/mpsoc/` (PL-as-hardware timing closure)
- Platform overlay: `platforms/fpga/`
- Facets key: none yet — **gap**: no `fpga` platform in the facets vocabulary; engage via `--platform soc` until the vocabulary is extended
- Engage: `python -m axiom_cli engage --domain <domain>` (full slice, filter manually)
- Gates: timing closure reports, bitstream versioning, PL/SW interface contracts
