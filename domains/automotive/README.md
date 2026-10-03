# automotive domain pack

Domain overlay: how the tool chain resolves a user prompt to automotive
skills, which skills engage per platform, and how the project's lifecycle
stage is determined. Domain overlay only — public references, project-authored
interpretations, applicability maps, workflows and examples. No licensed
normative standards text (`standards_are_metadata_only: true`).

## 1. Prompt → domain → skills (how selection works)

```
user prompt ──► route() ──► agent (debugging, implementation, …)
      │          packages/agents/router.py
      ▼
  detect_domain() ──► "automotive" ──► engage(domain, platform)
      │                                     packages/skills/engage.py
      │                                     registries/skill-index.json facets
      ▼
  context_files: skills/<id>/SKILL.md loaded graph-first
```

- `axiom run "<request>" --domain automotive --platform mcu` — explicit;
  `domain_source: explicit`.
- `axiom run "<request>"` — domain auto-detected from distinctive keywords
  (ASIL, HARA, SOTIF, UDS, MISRA, AUTOSAR, ASPICE, ECU, OBD, DoIP, ADAS,
  TARA, SecOC, FlexRay, J1939, SOME/IP, CAN-FD, V2X, ISO 21434/26262/21448,
  R155/R156, QNX, AAOS, BCM, PEPS …); `domain_source: detected`.
  Generic words (`can`, `code`, `body`, `cal`) never trigger detection.
  Explicit `--domain` always wins over detection.
- Matching rule: a skill engages when `"all"` is in its facets or the
  requested value is listed (`packages/skills/engage.py`).
- Profiles (`profiles/*.yaml`) engage by intersecting domains/platforms.

## 2. Automotive skill engagement matrix

`axiom engage --domain automotive --platform <p>`:

| Skill | mcu | autosar-classic | mpu | soc / mpsoc | autosar-adaptive | bare-metal / rtos / linux |
|---|---|---|---|---|---|---|
| automotive-spice (`all`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| automotive-vcycle (`all`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| automotive-cybersecurity (`all`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| automotive-body | ✓ | ✓ | – | – | – | – |
| automotive-coding | ✓ | ✓ | ✓ | – | ✓ | ✓ (bare-metal/rtos) |
| automotive-diagnostics | ✓ | ✓ | ✓ | – | ✓ | – |
| automotive-networks | ✓ | ✓ | ✓ | – | ✓ | – |
| automotive-ota | ✓ | ✓ | ✓ | – | ✓ | – |
| adas | – | – | ✓ | ✓ | ✓ | – |
| automotive-cockpit | – | – | ✓ | ✓ | – | – |
| automotive-middleware | – | – | ✓ | ✓ (soc) | ✓ | ✓ (linux) |

`--platform mcu` engages 8 of the 11 (all except adas/cockpit/middleware).

## 3. Project stage (declared + detected)

- Declared: profiles set `lifecycle:` + `entry:` (e.g.
  `profiles/automotive-mcu.yaml`: `v-model` / `implementation_available`
  → start phase `unit-verification` via `packages/workflow/entry.py`).
- Detected (heuristic): `axiom stage <path> [--profile <yaml>]` scans for
  lifecycle evidence — `requirements/` → concept, `architecture/` →
  system-architecture, `src/`/`headers/`/`design/` → detailed-design,
  `tests/` → unit-verification, `evidence/`/`validation/` → verification,
  `changelog.md` → maintenance — and reconciles with the declaration.
  Declaration wins on conflict (`conflict: true`); detection is advisory.
- Inventory ("what the project has/needs"): `axiom status` (skill versions,
  stale/missing flags, counts) + `axiom engage` (needed skills for the
  domain/platform pair).

## 4. Skill set

Process: `automotive-spice`, `automotive-vcycle`, `automotive-coding`.
Domains: `adas`, `automotive-body`, `automotive-cockpit`,
`automotive-middleware`, `automotive-networks`.
Assurance: `automotive-cybersecurity` (with `safety`, `security`).
Vehicle interface: `automotive-diagnostics`, `automotive-ota`.
Load the domain overlay plus task-specific skills before execution.
