# Composition: automotive + MCU + FreeRTOS + ARM

Example combination per `Feature.md`. Compositions derive — they never duplicate:
layer pointers resolve to skills, overlays, and facets; the engage slice is
computed live, not snapshotted.

| Dimension | Choice | Canonical source |
|-----------|--------|------------------|
| Domain | automotive | `domains/automotive/` |
| Technology | MCU | `technologies/mcu/LAYER.md` → `skills/mcu/` |
| OS | FreeRTOS | `os/freertos/LAYER.md` → `skills/rtos/` |
| Platform | ARM Cortex-M | `platforms/arm-cortex-m/` |

## Engage

```bash
python -m axiom_cli engage --domain automotive --platform mcu
python -m axiom_cli engage --domain automotive --platform rtos
```

## Derived requirements (summary; details in linked skills)

- ISO 26262 ASIL-rated safety goals (`safety` §3–§4) + MISRA C:2025 (`implementation` §2)
- AUTOSAR Classic BSW where the ECU integrates vehicle networks (`autosar`); FreeRTOS tasks for the control path (`rtos` §5)
- Static allocation, MPU partitioning, watchdog + safe-state per FTTI

## Gate checklist

- [ ] HARA + ASIL assignment with rationale (`safety` §7 gate 1)
- [ ] Traceability chain gap-free (`requirements-traceability`)
- [ ] MC/DC at ASIL D, fault-injection campaign on safe-state transitions
- [ ] Independent safety assessment recorded; human approval on file
