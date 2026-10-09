# OS layer: ROS 2

Pointer layer per `Feature.md`. Canonical content lives in the skill and the
platform overlay — this file only links them. Single source of truth:
`registries/skill-facets.yaml` + `registries/skill-index.json`.

- Skill: `skills/robotics/` (v1.2.0) — distro policy, interface-first architecture, real-time paths, simulation-first testing
- Platform overlay: `platforms/ros2/`
- Facets key: `platforms: [linux]` + `domains: [robotics]` (Kilted current, Jazzy LTS to 2029, Humble to 2027)
- Engage: `python -m axiom_cli engage --platform linux --domain robotics`
- Gates: distro pinned with EOL trigger, DDS QoS per topic, control-path determinism measured
