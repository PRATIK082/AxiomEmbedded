# Composition: robotics + SoC + Linux + ARM

Example combination per `Feature.md`. Compositions derive — they never duplicate:
layer pointers resolve to skills, overlays, and facets; the engage slice is
computed live, not snapshotted.

| Dimension | Choice | Canonical source |
|-----------|--------|------------------|
| Domain | robotics | `domains/robotics/` |
| Technology | SoC | `technologies/soc/LAYER.md` → `skills/soc/` |
| OS | embedded Linux + ROS 2 | `os/embedded-linux/LAYER.md`, `os/ros2/LAYER.md` |
| Platform | ARM Cortex-A | `platforms/arm-cortex-a/` |

## Engage

```bash
python -m axiom_cli engage --domain robotics --platform linux
python -m axiom_cli engage --domain robotics --platform soc
```

## Derived requirements (summary; details in linked skills)

- ROS 2 distro pinned (Kilted current / Jazzy LTS); DDS QoS per topic (`robotics` §3.4)
- Yocto Wrynose 6.0 image, verified boot + A/B OTA (`embedded-linux` §3, §6)
- Safety island or RTOS coprocessor for hard control loops (`soc`, `rtos`)

## Gate checklist

- [ ] Simulation suite green (nominal + degraded + adversarial)
- [ ] Bag-regression metrics within thresholds
- [ ] OTA update + rollback + power-loss tests pass on hardware
- [ ] Perception/ML nodes routed through `ai-validation` where safety-relevant
