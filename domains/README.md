# Domains

Domain overlays provide context, applicability metadata and domain-specific hooks.
They do not own lifecycle orchestration.

## Domain Engineering Skill Architecture (DESA)

Each domain directory may contain:

| File | Purpose |
|------|---------|
| `manifest.json` | Domain overlay manifest (existing) |
| `README.md` | Domain overview and guidance |
| `domain-profile.yaml` | Domain profile: standards, platforms, languages, risk classes, skill families |
| `skill-family-map.yaml` | Maps engineering activities to skill IDs for this domain |

## Reference domains (fully profiled)

- `automotive/` — ISO 26262, ISO/SAE 21434, Automotive SPICE, AUTOSAR
- `aerospace/` — DO-178C, DO-254, ARP4754/4761
- `industrial/` — IEC 61508, IEC 62061, ISO 13849, IEC 62443
- `robotics/` — ISO 10218-1/2, IEC 61508, IEC 62061

## Remaining domains (profile pending)

consumer, defense, energy, generic-embedded, iot, marine, medical, rail,
semiconductor, space, telecom

## Taxonomies

- `taxonomies/activities.yaml` — 30 engineering activities across 12 families
- `taxonomies/skill-types.yaml` — 7 capability kinds
- `taxonomies/relationship-semantics.yaml` — 16 relationship types

## Standards registry

- `standards/registry.yaml` — 24 standards with lifecycle state (published/draft/pre-release/proposed/withdrawn/superseded)
