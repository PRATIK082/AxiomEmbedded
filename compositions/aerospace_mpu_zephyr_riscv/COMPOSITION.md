# Composition: aerospace + MPU + Zephyr + RISC-V

Example combination per `Feature.md`. Compositions derive — they never duplicate:
layer pointers resolve to skills, overlays, and facets; the engage slice is
computed live, not snapshotted.

| Dimension | Choice | Canonical source |
|-----------|--------|------------------|
| Domain | aerospace | `domains/aerospace/` |
| Technology | MPU | `technologies/mpu/LAYER.md` → `skills/mpu/` |
| OS | Zephyr | `os/zephyr/LAYER.md` → `skills/rtos/` |
| Platform | RISC-V | `platforms/risc-v/` |

## Engage

```bash
python -m axiom_cli engage --domain aerospace --platform mpu
python -m axiom_cli engage --domain aerospace --platform rtos
```

## Derived requirements (summary; details in linked skills)

- DAL-rated objectives per DO-178C Annex A (`safety` §3.3); MMU/MPU partitioning for robustness
- Zephyr devicetree + west manifest pinned; board config versioned
- Deterministic control path measured (jitter/latency) or delegated to a safety MCU

## Gate checklist

- [ ] DAL allocation with independence argument where required
- [ ] Tool qualification per DO-330 TQL mapping
- [ ] HIL campaign on target ISA (RISC-V) before flight-credit claims
- [ ] Human approval on file for safety-significant releases
