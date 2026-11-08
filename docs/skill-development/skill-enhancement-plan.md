# Skill Enhancement Plan — AxiomEmbedded

**Status:** Phase 4/5 proposal. **No bulk implementation has been started.**
Approval required before Phase 6.

## 1. Guiding principles

1. Maintain existing AxiomEmbedded skill hierarchy and registry conventions
   (`skills/<id>/SKILL.md` + `manifest.yaml`, `registries/skills.json`,
   `registries/skill-facets.yaml`, `skills/catalog.yaml`, `skills/registry.yaml`).
2. No parallel skill system. No duplicate IDs. No orphan skills.
3. All new content independently authored; no copied external text.
4. Generic skills remain domain-neutral; domain overlays apply separately.
5. Hardware facts come from manufacturer documentation, never invented.
6. Build success != hardware correctness.

## 2. Prioritized implementation batches (per task spec section 16)

### Batch 1 — Generic hardware and peripheral engineering (highest priority)
- Enhance `drivers` (GPIO, UART, SPI, I2C, timers, ADC, PWM, RTC, storage,
  HMI, actuators, termination, pull-ups) with structured subsections.
- Create `sensor-acquisition` parent + 6 subskills.
- Add `hardware-aware-checks` capability (pin/peripheral/DMA/clock conflicts,
  voltage/logic-level, resource exhaustion).
- Enhance `hardware-architecture` (pin mux, electrical compatibility, power).
- Enhance `mcu` (clock tree, DMA, interrupts, low-power, NVM).

### Batch 2 — MCU and firmware implementation
- Enhance `bare-metal` (watchdog, fault handlers detail).
- Enhance `embedded-c`/`embedded-cpp` (register discipline cross-refs).
- Create framework skills: `framework-arduino`, `framework-esp-idf`,
  `framework-zephyr` (or fold Zephyr into platform + rtos).
- Enhance `rtos` (FreeRTOS/Zephyr specifics).
- Enhance `bootloader` (flash programming detail).

### Batch 3 — Sensor and communication integration
- Wire `sensor-acquisition` subskills to `drivers`, `unit-test`, `validation`.
- Add integration-test HSI validation guidance.
- Add actuator/motor/encoder subskills.

### Batch 4 — Hardware-aware debugging
- Enhance `debugging` (watchdog resets, brownout, power failures, auto
  compile-and-retry guidance).
- Enhance `performance` (timing/power verification).

### Batch 5 — Build and hardware validation
- Add validation-levels taxonomy (source/build/static/host/sim/HIL/physical).
- Enhance `validation`, `simulation`, `test-automation`, `integration-test`.
- Enhance `axiom-mil-sil-hil-testing` / `axiom-hil-test-planning`.
- Enhance `hardware-bringup` (wiring verification, deviation logs).

### Batch 6 — Framework-specific enhancements
- Framework skills content (idioms, toolchain, build, debug).
- Cross-ref to `build-system`, `embedded-linux`.

### Batch 7 — Skill benchmarking
- Extend `evaluation/` with embedded peripheral tasks (EV-embedded-*).
- Add evaluation comparing skill levels (none / existing / enhanced).
- Add `skill-evaluation` methodology doc.

## 3. New skills to introduce (pending approval)

| Proposed skill ID | Type | Parent | Maturity target | Justification |
|---|---|---|---|---|
| sensor-acquisition | parent | (new top-level) | experimental | No generic sensor capability exists; drivers is too broad |
| sensor-driver-integration | subskill | sensor-acquisition | experimental | Reusable sensor driver integration pattern |
| sampling-and-timestamping | subskill | sensor-acquisition | experimental | Sampling sync/timestamping gap |
| sensor-calibration | subskill | sensor-acquisition | experimental | Calibration guidance gap |
| digital-filtering | subskill | sensor-acquisition | experimental | Filtering/noise reduction gap |
| sensor-diagnostics | subskill | sensor-acquisition | experimental | Sensor fault detection gap |
| multi-sensor-synchronization | subskill | sensor-acquisition | experimental | Multi-sensor sync gap |
| hardware-aware-checks | skill | (new) | experimental | No conflict-detection capability exists |
| framework-arduino | skill | (new) | experimental | No Arduino framework skill exists |
| framework-esp-idf | skill | (new) | experimental | No ESP-IDF skill exists |
| framework-zephyr | skill | (new) or platform overlay | experimental | Zephyr coverage only via platform/rtos |
| peripheral-timers | subskill | drivers | experimental | Timer/PWM/RTC gap |
| storage-and-memory | subskill | drivers | experimental | SD/external flash/EEPROM gap |
| hmi-and-actuators | subskill | drivers | experimental | Keypad/display/motor/encoder gap |
| validation-levels | doc+skill | validation | experimental | Build != hardware proof distinction |

## 4. Registries to update (when implementing)

- `registries/skills.json` (add new skill entries).
- `registries/skill-facets.yaml` (descriptions, domains, platforms).
- `skills/catalog.yaml` and `skills/registry.yaml`.
- `registries/agent-domain-matrix.json` (skill-agent links).
- `agents/*/manifest.json` skill_binding where applicable.
- `configs/domain-routing.yaml` (if skill routing needed).

## 5. Agent integrations

Connect new/enhanced skills to existing agents:

- `hardware-architecture` agent: hardware-aware-checks, hardware-architecture skill.
- `implementation` agent: drivers, sensor-acquisition, framework skills.
- `code-review` agent: drivers, embedded-c, framework skills.
- `debugging` agent: debugging skill, hardware-aware-checks.
- `test-engineering` agent: unit-test, integration-test, validation-levels.
- `hardware-bringup` agent: hardware-bringup, hardware-aware-checks.
- `skill-orchestrator` / `skill-researcher` / `skill-implementer` / `skill-verifier`:
  orchestrate the new skills.

## 6. Ruleset integrations

- Add rules for: pin conflict detection, peripheral conflict, DMA conflict,
  clock conflict, resource exhaustion, unsupported peripheral, invalid framework
  combination, voltage incompatibility, timing incompatibility.
- Location: `rules/` (machine-readable project controls).

## 7. Profile mappings

- Add embedded peripheral profiles? Possibly a `profiles/embedded-peripherals.yaml`
  composition (subject to existing profile schema). Defer to implementation.

## 8. Workflow mappings

- No new lifecycle workflows needed; skills attach to existing workflows
  (greenfield, brownfield, feature-change, defect-fix).

## 9. CI changes

- Extend `scripts/validate_skills.py` checks for new required sections
  (validation methodology, acceptance criteria, evidence).
- Add duplicate-content check, broken-link check for new skills.
- Add evaluation tasks EV-embedded-* and run in CI where hardware available
  (mark hardware-dependent tests clearly; do not falsely report as executed).

## 10. Documentation changes

- `REPOSITORY_INVENTORY.md` counts update.
- `README.md` skill counts update.
- `docs/skills/*` authoring guide references.
- `docs/skill-development/*` (these files).

## 11. Estimated implementation scope

- Batch 1-2: ~12-18 new/enhanced skills, ~40-60 files.
- Batch 3-5: ~10 skills/docs.
- Batch 6-7: framework skills + evaluation tasks.
- Total: significant; must be done in small, reviewable PRs per CONTRIBUTING.md.

## 12. Approval checkpoint (Phase 5)

**Presented for approval:**

Existing skills to modify (enhance):
- drivers, mcu, bare-metal, hardware-architecture, hardware-bringup,
  debugging, performance, validation, simulation, test-automation,
  integration-test, embedded-c, embedded-cpp, rtos, bootloader, unit-test.

New skills to introduce:
- sensor-acquisition (+ 6 subskills), hardware-aware-checks,
  framework-arduino, framework-esp-idf, framework-zephyr,
  peripheral-timers, storage-and-memory, hmi-and-actuators (as subskills),
  validation-levels.

Subskills to introduce:
- Listed under sensor-acquisition and drivers.

Registries to update:
- skills.json, skill-facets.yaml, catalog.yaml, registry.yaml,
  agent-domain-matrix.json.

Agent integrations:
- hardware-architecture, implementation, code-review, debugging,
  test-engineering, hardware-bringup, skill-* agents.

Ruleset integrations:
- New hardware-aware conflict rules.

CI changes:
- validate_skills extensions, EV-embedded-* tasks, duplicate/broken-link checks.

Documentation changes:
- REPOSITORY_INVENTORY, README, docs/skill-development, docs/skills.

Estimated implementation scope:
- ~25-35 skill packages across 7 batches; multi-PR.

**Awaiting approval before starting bulk implementation.**

Until approval, only the discovery documents in `docs/skill-development/` are
added. No skill files, registries, or code are modified.
