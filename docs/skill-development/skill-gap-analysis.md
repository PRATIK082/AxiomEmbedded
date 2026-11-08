# Skill Gap Analysis — IoT-SkillsBench vs AxiomEmbedded

**Status:** Phase 3 gap analysis (discovery only; no implementation yet).
**Decisions legend:** E = Enhance existing skill; S = Add subskill; N = Create new
skill; C = Cross-reference; NA = Not applicable.

## 1. Method

For each capability demonstrated by the reference repository, we identify the
closest existing AxiomEmbedded skill (from `registries/skill-facets.yaml`,
185 catalog skills), classify the gap, and propose an independently authored
change. Existing skills are **not** duplicated; gaps are filled only where no
equivalent capability exists or where guidance is materially incomplete.

## 2. Existing embedded-relevant Axiom skills (baseline)

From `registries/skill-facets.yaml`, the embedded-relevant skills (platforms
mcu/mpu/soc/mpsoc/bare-metal/rtos/linux or domains generic-embedded/iot) are:

ai-validation, autosar, bare-metal, bootloader, drivers, edge-ai, embedded-c,
embedded-cpp, embedded-linux, fault-injection, hardware-architecture,
hardware-bringup, mcu, mpsoc, mpu, robotics, rtos, rust-embedded, safety,
security, soc, (plus cross-cutting: debugging, build-system, unit-test,
integration-test, system-test, validation, simulation, performance,
configuration-management, change-impact, release, evidence, traceability,
requirements, architecture, software-architecture, implementation, code-review,
static-analysis, test-automation, coverage, legacy-recovery, documentation).

## 3. Capability-by-capability gap table

| # | Reference capability | Existing Axiom skill | Gap | Decision | Proposed change | Validation |
|---|---|---|---|---|---|---|
| 1 | MCU architecture fundamentals | mcu | Partial: core selection/startup covered; register/clock/DMA detail shallow | E | Expand mcu with clock/reset/DMA/interrupt controller subsections | checklist + review |
| 2 | Memory-mapped registers | drivers | Covered (register discipline) | C | Cross-ref drivers from mcu/embedded-c | link check |
| 3 | Clock/reset configuration | mcu, drivers | Shallow | E | Add clock-tree guidance to mcu + drivers | checklist |
| 4 | GPIO configuration | drivers | Generic only; no pin-mux/debounce specifics | E | Add GPIO configuration subsection to drivers | unit tests |
| 5 | Pin multiplexing | hardware-architecture | Mentioned, not detailed | E | Expand hardware-architecture HSI/pin-mux | review |
| 6 | Interrupt controller | bare-metal, drivers | ISR discipline covered; NVIC specifics shallow | E | Add interrupt-priority/DMA-channel guidance | review |
| 7 | DMA architecture | drivers | DMA contracts covered | C | Cross-ref; add DMA conflict checks to hardware-aware checks | link check |
| 8 | Timers/counters | drivers | Not dedicated | S | Add `peripheral-timers` subskill under drivers or new `embedded-timing` | checklist |
| 9 | Watchdog | bare-metal, safety | Partial | E | Add watchdog configuration to bare-metal | review |
| 10 | ADC | drivers | Generic mention | S | Add `adc-acquisition` subskill under a new sensor-acquisition parent | unit tests |
| 11 | DAC | drivers | Not covered | S | Add DAC subskill | checklist |
| 12 | PWM | drivers | Not covered | S | Add PWM subskill (actuator control) | checklist |
| 13 | Memory management (flash/EEPROM/NVM) | bootloader, mcu | Partial | E | Expand mcu/bootloader with NVM/flash programming | review |
| 14 | Boot/startup | bare-metal, bootloader | Covered | C | Cross-ref | link check |
| 15 | Low-power modes | mcu, performance | Not dedicated | E | Add low-power section to mcu | review |
| 16 | Hardware abstraction / BSP | drivers, hardware-architecture | BSP mentioned | E | Formalize BSP abstraction guidance in drivers | review |
| 17 | Board support packages | hardware-bringup | Bringup covered; BSP structure shallow | E | Add BSP structure to hardware-bringup | review |
| 18 | UART | drivers | Bus abstraction covered; protocol specifics shallow | E | Add UART engineering subsection to drivers | checklist |
| 19 | SPI | drivers | Covered at bus-abstraction level | E | Add SPI timing/mode guidance | checklist |
| 20 | I2C | drivers | Covered at bus-abstraction level | E | Add I2C clock-stretch/termination guidance | checklist |
| 21 | CAN / CAN FD | axiom-can-network-design, axiom-can-stack-integration | Covered (automotive) | C | Cross-ref generic drivers to CAN skills | link check |
| 22 | USB | drivers | Not dedicated | N? | Defer: create only if concrete demand; mark gap | backlog |
| 23 | Ethernet | axiom-automotive-ethernet-someip | Automotive only | N? | Defer generic ethernet skill | backlog |
| 24 | BLE / Wi-Fi | edge-ai? no | Not covered | N? | Defer; IoT overlay candidate | backlog |
| 25 | GPIO expanders | drivers | Not covered | S | Subskill under drivers | checklist |
| 26 | External interrupts | bare-metal, drivers | Covered partially | E | Expand | review |
| 27 | RTC | drivers | Not dedicated | S | Add RTC subskill (timekeeping) | checklist |
| 28 | SD card | drivers | Not dedicated | S | Add storage (SD/flash) subskill | checklist |
| 29 | External flash | drivers | Not dedicated | S | Storage subskill covers | checklist |
| 30 | Touch/keypads/displays | drivers | Not covered | S | Add HMI subskill (keypad/display) | checklist |
| 31 | Sensors | drivers | Generic | N | Create `sensor-acquisition` parent skill (new) | checklist + tests |
| 32 | Actuators/motor controllers/encoders | drivers | Not covered | S | Add actuator/motor subskill under drivers or new `actuator-control` | checklist |
| 33 | Communication transceivers | drivers, hardware-architecture | Partial | E | Expand | review |
| 34 | Sensor init/device ID/register config | drivers | Partial | E (via sensor-acquisition) | sensor-acquisition subskills | tests |
| 35 | Sampling frequency | performance, rtos | Partial | E | Add sampling/timestamping to sensor-acquisition | tests |
| 36 | Calibration | validation | Not dedicated | S | sensor-calibration subskill | tests |
| 37 | Filtering/noise reduction/signal processing | performance | Not dedicated | S | digital-filtering subskill | tests |
| 38 | Measurement accuracy | validation | Partial | E | Add accuracy to sensor-acquisition | review |
| 39 | Sensor diagnostics/fault detection | debugging, fault-injection | Partial | E | sensor-diagnostics subskill | tests |
| 40 | Sensor fusion | edge-ai? no | Not covered | N? | Defer (advanced) | backlog |
| 41 | Data conversion/timestamp/sync | sensor-acquisition | Not covered | S | sampling-and-timestamping subskill | tests |
| 42 | Driver architecture | drivers | Covered | C | - | link check |
| 43 | HAL design | drivers, software-architecture | Covered | C | - | link check |
| 44 | BSP architecture | hardware-architecture | Partial | E | Expand | review |
| 45 | Device abstraction | drivers | Covered (bus interfaces) | C | - | link check |
| 46 | Peripheral ownership/resource mgmt | drivers | Partial (resource arbitration) | S | peripheral-resource-arbitration subskill | checklist |
| 47 | Interrupt-driven design | bare-metal, drivers | Covered | C | - | link check |
| 48 | Polling vs interrupt | drivers | Not explicit | E | Add decision guidance | review |
| 49 | DMA-driven design | drivers | Covered | C | - | link check |
| 50 | Event-driven architecture | software-architecture, rtos | Covered | C | - | link check |
| 51 | State machines | software-architecture | Covered | C | - | link check |
| 52 | Non-blocking firmware | drivers, bare-metal | Covered (RTOS isolation) | C | - | link check |
| 53 | Concurrency/synchronization | rtos, software-architecture | Covered | C | - | link check |
| 54 | Real-time scheduling/timing analysis | rtos, performance | Covered | C | - | link check |
| 55 | Memory optimization | performance, embedded-c | Covered | C | - | link check |
| 56 | Power optimization | performance, mcu | Partial | E | Add power section to mcu | review |
| 57 | Bare-metal C/C++ | embedded-c, embedded-cpp, bare-metal | Covered | C | - | link check |
| 58 | Arduino framework | (none dedicated) | Not covered | N (framework skill) | Create `framework-arduino` skill (new) | checklist |
| 59 | ESP-IDF | (none dedicated) | Not covered | N | Create `framework-esp-idf` skill | checklist |
| 60 | Zephyr RTOS | zephyr? platforms/zephyr exists but skill? | Partial (rtos generic) | E/N | Add Zephyr-specific skill or platform overlay | checklist |
| 61 | FreeRTOS | rtos | Covered generically | C/E | Add FreeRTOS specifics to rtos | review |
| 62 | Embedded Linux | embedded-linux | Covered | C | - | link check |
| 63 | PlatformIO | build-system | Not covered | N? | Defer (tooling) | backlog |
| 64 | CMake-based firmware | build-system | Covered | C | - | link check |
| 65 | Vendor SDKs | drivers, mcu | Partial | E | Add vendor-SDK guidance to mcu | review |
| 66 | Board-specific frameworks | platforms/* | Covered via platforms | C | - | link check |
| 67 | Pin assignment/conflict detection | hardware-architecture, drivers | Not modeled | N | Create `hardware-aware-checks` skill/capability | tests |
| 68 | Peripheral conflict detection | hardware-architecture | Not modeled | N (same as above) | part of hardware-aware-checks | tests |
| 69 | Voltage/logic-level compatibility | hardware-architecture | Not modeled | E | Add electrical compatibility to hardware-architecture | review |
| 70 | Pull-up/down requirements | drivers (I2C) | Partial | E | Add to drivers I2C section | checklist |
| 71 | Bus termination | drivers | Not covered | E | Add to drivers | checklist |
| 72 | Power budget | hardware-architecture | Covered | C | - | link check |
| 73 | Clock compatibility | mcu | Partial | E | Add | review |
| 74 | Timing constraints | performance | Covered | C | - | link check |
| 75 | Interrupt priority | bare-metal, drivers | Partial | E | Expand | review |
| 76 | DMA channel conflicts | drivers | Not modeled | E (hardware-aware-checks) | part of #67 | tests |
| 77 | Resource utilization | performance | Covered | C | - | link check |
| 78 | Wiring verification | hardware-bringup | Partial | E | Add wiring verification checklist | checklist |
| 79 | HW config documentation | hardware-architecture | Covered | C | - | link check |
| 80 | HW/SW interface validation | integration-test | Partial | E | Add HSI validation to integration-test | tests |
| 81 | Startup failures | debugging, hardware-bringup | Covered | C | - | link check |
| 82 | Peripheral init failures | debugging, drivers | Covered | C | - | link check |
| 83 | Communication failures | debugging | Covered | C | - | link check |
| 84 | Interrupt failures | debugging | Covered | C | - | link check |
| 85 | DMA failures | debugging, drivers | Covered | C | - | link check |
| 86 | Stack overflow/heap exhaustion | debugging, performance | Covered | C | - | link check |
| 87 | Memory corruption | debugging | Covered | C | - | link check |
| 88 | Race conditions | debugging, rtos | Covered | C | - | link check |
| 89 | Timing failures | debugging, performance | Covered | C | - | link check |
| 90 | Watchdog resets/brownout | debugging | Covered partially | E | Add to debugging | review |
| 91 | Hard/bus faults | debugging, bare-metal | Covered | C | - | link check |
| 92 | Deadlocks | debugging, rtos | Covered | C | - | link check |
| 93 | Power-related failures | debugging | Partial | E | Add | review |
| 94 | HW/SW integration failures | debugging, integration-test | Covered | C | - | link check |
| 95 | Driver unit tests | unit-test, drivers | Covered | C | - | link check |
| 96 | HAL mocking | unit-test, drivers | Covered (mockable seams) | C | - | link check |
| 97 | Host-based tests | unit-test | Covered | C | - | link check |
| 98 | Peripheral simulation | simulation | Covered | C | - | link check |
| 99 | Integration tests | integration-test | Covered | C | - | link check |
| 100 | SIL | simulation, axiom-mil-sil-hil-testing | Covered | C | - | link check |
| 101 | HIL | axiom-hil-test-planning, axiom-mil-sil-hil-testing, test-automation | Covered | C | - | link check |
| 102 | Board-level testing | hardware-bringup, validation | Covered | C | - | link check |
| 103 | Regression testing | test-automation, change-impact | Covered | C | - | link check |
| 104 | Timing verification | performance | Covered | C | - | link check |
| 105 | Power verification | hardware-architecture | Partial | E | Add power verification | review |
| 106 | Fault injection | fault-injection | Covered | C | - | link check |
| 107 | Coverage analysis | coverage | Covered | C | - | link check |
| 108 | Hardware acceptance tests | validation, axiom-robot-acceptance-protocol | Covered | C | - | link check |
| 109 | Test result evidence | evidence | Covered | C | - | link check |
| 110 | Skill discovery/loading (registry) | packages/skills/*, registries/* | Covered (Axiom richer) | C | - | tests |
| 111 | Skill composition | skill-orchestrator agent, skill-facets | Covered | C | - | tests |
| 112 | Code generation methodology | implementation, agents | Covered (Axiom richer) | C | - | tests |
| 113 | Build/compile validation | build-system, test-automation | Covered | C | - | tests |
| 114 | Hardware programming (flash) | bootloader, hardware-bringup | Covered | C | - | tests |
| 115 | Debugging/retry mechanisms | debugging, auto_test concept | Partial (no auto retry) | E | Add compile-and-retry guidance to debugging/build-system | review |
| 116 | Benchmark task definitions | evaluation/tasks | Covered (EV-*) | E | Extend evaluation tasks for embedded peripheral scenarios | tests |
| 117 | Skill quality differences (human vs LLM) | skill-quality-gates.md | Covered conceptually | E | Add evaluation comparing skill levels | tests |
| 118 | Source-level vs build vs static vs host vs sim vs HIL vs physical acceptance | validation, simulation | **Not distinguished** | N/E | Create validation-level taxonomy doc + skill guidance | tests |

## 4. Genuine new-skill candidates (only where no equivalent exists)

1. `sensor-acquisition` (parent) + subskills: sensor-driver-integration,
   sampling-and-timestamping, sensor-calibration, digital-filtering,
   sensor-diagnostics, multi-sensor-synchronization.
2. `hardware-aware-checks` (or extend `hardware-architecture`): pin/peripheral/DMA/
   clock conflict detection, voltage/logic-level compatibility, resource
   exhaustion, unsupported-peripheral detection.
3. `framework-arduino` (framework skill).
4. `framework-esp-idf` (framework skill).
5. `framework-zephyr` (framework skill) — may be folded into platform overlay +
   rtos skill instead; decide in plan.
6. `peripheral-timers` / `embedded-timing` (timer/PWM/RTC) — could be subskills
   of `drivers`.
7. `storage-and-memory` (SD/external flash/EEPROM/NVM) — subskill of drivers or
   new.
8. `hmi-and-actuators` (keypad/display/motor/encoder) — subskill of drivers.
9. `validation-levels` taxonomy (source/build/static/host/sim/HIL/physical) —
   could be a doc + enhancement to `validation`/`simulation`/`test-automation`.
10. `skill-evaluation` (benchmarking methodology) — extend `evaluation/` and
    `ai-validation`.

## 5. Cross-references to add (no new content)

- `drivers` <-> `mcu`, `embedded-c`, `hardware-architecture`, `bare-metal`.
- `sensor-acquisition` (new) <-> `drivers`, `unit-test`, `validation`,
  `performance`.
- Framework skills <-> `drivers`, `build-system`, `embedded-linux`, `rtos`.
- `hardware-aware-checks` <-> `hardware-architecture`, `drivers`, `rules/*`.
- Validation-levels <-> `validation`, `simulation`, `test-automation`,
  `integration-test`, `axiom-mil-sil-hil-testing`.

## 6. Explicitly NOT applicable (NA)

- Cloning the reference's Arduino-only auto pin-mapping heuristic as a core
  feature (Axiom should model pins via hardware definitions, not heuristics).
- Importing benchmark tasks verbatim (license + attribution; rewrite as
  Axiom evaluation tasks).
- IoT-only framing; Axiom remains domain-neutral.
- Treating compilation as hardware proof (Axiom must keep the distinction).

## 7. Summary counts

- Enhance (E): ~35 capabilities.
- Add subskill (S): ~15.
- Create new skill (N): ~10 candidates (pending approval).
- Cross-reference (C): ~45.
- Not applicable (NA): ~6.
- Deferred/backlog: USB, Ethernet, BLE/Wi-Fi, sensor fusion, PlatformIO.

All decisions are proposals pending the approval checkpoint (Phase 5).
