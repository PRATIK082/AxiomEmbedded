# IoT-SkillsBench Study — AxiomEmbedded Reference Research

**Status:** Phase 2 reference research (discovery only; no implementation yet).
**Reference repository:** https://github.com/iot-agent/iot-skillsbench (Apache-2.0, arXiv:2603.19583).
**Target repository:** AxiomEmbedded (this repo).
**Branch:** `feat/embedded-skills-intelligence-initiative`.

This document records engineering knowledge extracted from the reference repository.
It does **not** reproduce source files, skill text, or benchmark tasks. All content
here is independently authored analysis. See `source-and-license-register.md`.

## 1. Reference repository overview

IoT-SkillsBench is the companion codebase for the paper "Skilled AI Agents for
Embedded and IoT Systems Development" (Li et al., 2026). It demonstrates a
skills-based agentic AI framework for embedded/IoT code generation and a
benchmark for evaluating agents under three skill levels.

Key quantitative claims (from README):

- 3 platform/framework combinations, 23 peripherals, 42 tasks, 3 difficulty levels.
- 378 hardware-in-the-loop (HIL) experiments.
- Three agent configurations compared per task: no-skills, LLM-generated skills,
  human-expert skills. Human-expert skills achieve near-perfect success.
- Skills are plain Markdown files with YAML frontmatter (`name`, `description`),
  loaded by a `SkillRegistry` (`src/loader.py`) and selected by a manager LLM node.

## 2. Boards, frameworks, peripherals (reference scope)

Boards/frameworks tested (from `docs/boards-peripherals.md`):

| Board | Framework |
|---|---|
| ATmega2560 (Arduino Mega 2560 Rev3) | Arduino (CLI v1.4.1, core arduino:avr v1.8.7) |
| ESP32-S3 (ESP32-S3-BOX-3) | ESP-IDF v5.1.2 |
| nRF52840 (Arduino Nano 33 BLE Rev2) | Zephyr via nRF Connect SDK v2.7.0 |

Peripherals tested (23): LED, push button, active/passive buzzer, relay, laser
emitter, rotary encoder, 4x4 keypad, tilt switch, analog joystick, photoresistor,
TMP36, water-level sensor, PIR, ultrasonic HC-SR04, digital sound/shock sensors,
DHT11, DS18B20, LCD1602 (HD44780), DS1307 RTC, MPU6050, BME280.

Skill sets shipped:

- `skills-human-expert/` — 30 curated skills (framework + peripheral).
- `skills-llm-generated/` — 33 LLM-generated skills (interface + peripheral, per
  board/framework variants).

## 3. Agentic architecture (reference)

LangGraph workflow (`src/graph.py`, `src/nodes.py`):

```
manager -> [pin_mapper] -> prepare_workspace -> coder -> assemble_artifacts -> persist -> END
```

- `manager_node`: scans skills, asks LLM to select relevant skills from the
  available list, loads combined skill content. Falls back to all skills on
  parse failure.
- `pin_mapper_node`: Arduino-only auto pin assignment from a wiring map.
- `coder_node`: generates code using skill content + requirements.
- Output: generated source + `manifest.lock.json`, `metadata.json`, `debug.json`.

Skill discovery (`src/loader.py`): `SkillRegistry` scans `SKILL.md`, `*.skill`,
and top-level `*.md` (excluding README), parses YAML frontmatter, caches bodies,
loads `resources/` subdirectory files (`.c/.h/.ino/.py/.cpp/.hpp`) into the
skill body.

## 4. Evaluation methodology (reference)

- Benchmark tasks per board/framework at 3 levels (`tasks/level1..3`).
- Three agent configurations compared: no-skills, LLM-generated skills,
  human-expert skills.
- Metrics: build success, runtime/HIL success on real hardware, token usage.
- Scripts: `run_task_single.py`, `batch_run.py`, `auto_test.py` (compile + retry,
  Arduino only).
- Key finding cited: structured human-expert skills reach near-perfect success
  without retrieval/long-context reasoning.

## 5. Engineering knowledge demonstrated (extracted concepts)

These are *concepts* extracted, not copied text:

### A. Hardware/MCU fundamentals
- Board-specific pinout and wiring discipline (analog/digital, power rails).
- Peripheral init sequences, register-level configuration (ESP-IDF register
  access, Zephyr devicetree).
- Clock/timer usage for sampling intervals.

### B. Peripheral engineering (interface-centric)
- GPIO (digital in/out, interrupts, debouncing).
- ADC (reading sensors, scaling).
- PWM (passive buzzer tones).
- UART (NMEA GPS, fingerprint sensor protocols).
- I2C (RTC, IMU, power sensor, UV sensor, ToF, NFC).
- SPI (microSD, BME280).
- 1-Wire (DHT11, DS18B20).

### C. Sensor and data acquisition
- Raw-to-engineering-unit conversion with sensitivity constants.
- Axis/sign convention documentation before control tuning.
- Normalization of accel/gyro by configured ranges.
- Sampling frequency and timestamp management.
- Sensor diagnostics and fault handling.

### D. Firmware architecture
- Interface-first device drivers (bus abstraction).
- Non-blocking, event-driven patterns.
- Debouncing patterns (software debouncing skill).
- Hardware timer driven sampling.

### E. Frameworks
- Arduino framework idioms (library-based).
- ESP-IDF (register/HAL, FreeRTOS tasks, ESP-IDF components).
- Zephyr (devicetree, Kconfig, workqueues).

### F. Hardware integration and validation
- Auto pin mapping for Arduino when task omits pins.
- Wiring verification via annotated diagrams.
- Compile + flash + serial monitor validation loop.
- HIL validation on real boards.

### G. Debugging and diagnostics
- Compile-and-retry loop (`auto_test.py`).
- Serial output verification.

### H. Testing and verification
- Build validation per platform toolchain.
- HIL acceptance on physical hardware.

## 6. Reference limitations (assessed)

1. **Narrow hardware scope.** Only 3 boards (AVR, ESP32-S3, nRF52840) and
   hobbyist peripherals. No automotive/industrial/aerospace/defense coverage.
2. **Framework coupling.** Skills are tightly bound to Arduino/ESP-IDF/Zephyr
   idioms; portability across vendors is limited.
3. **No safety/security.** No functional safety, cybersecurity, or
   certification-aware guidance; no HARA/ASIL/SIL concepts.
4. **No lifecycle/traceability.** No requirements traceability, V-model,
   change-impact, or evidence packaging.
5. **No industrial practices.** No MISRA/CERT, static analysis, code review
   governance, configuration management, or release engineering.
6. **No hardware-aware conflict checks.** No pin/peripheral/DMA/clock conflict
   detection model; pin mapping is a heuristic fallback.
7. **Verification conflated with compilation.** `auto_test.py` compile-and-retry
   does not distinguish source-level vs build vs HIL; a successful compile is
   implicitly treated as progress toward correctness.
8. **No abstraction of electrical constraints.** Voltage/logic-level, bus
   termination, power budget, timing constraints are not modeled.
9. **No reusability beyond IoT.** Skills are task-oriented (e.g. "mpu6050.md")
   rather than generic capability skills; composition is LLM-driven selection,
   not structured parent/child.
10. **Benchmark is HIL-dependent.** Reproducing 378 HIL experiments requires
    physical boards and toolchains; not CI-friendly.
11. **No provenance/attribution discipline.** Skills carry no license/source
    metadata beyond frontmatter name/description.
12. **LLM-generated skills are weaker.** The benchmark shows human-expert skills
    outperform; this validates Axiom's emphasis on curated, reviewed skills.

## 7. Licensing and provenance

- Reference repo license: Apache-2.0 (verified via `LICENSE` header and README
  badge). Full text in the cloned copy at
  `C:/Users/Pratik/AppData/Local/Temp/opencode/iot-skillsbench/LICENSE`.
- AxiomEmbedded is Apache-2.0. Compatible for concept-level inspiration.
- No third-party code or skill text will be imported. See
  `source-and-license-register.md`.

## 8. What Axiom already covers that the reference lacks

AxiomEmbedded already has domain-neutral, production-oriented skills that the
reference lacks entirely: functional safety, cybersecurity, MISRA/static
analysis, requirements traceability, V-model/V&V, code review, configuration
management, release, HIL planning, MIL/SIL/HIL testing, hardware bringup, RTOS
architecture, AUTOSAR, embedded Linux, robotics, edge AI, etc. These remain the
differentiators and must not be diluted.

## 9. Conclusion

The reference's value to Axiom is **methodological and motivational**, not
content: (1) a demonstration that curated human-expert skills outperform
LLM-generated ones; (2) a concrete skill-file format (Markdown + YAML
frontmatter) compatible with Axiom's existing SKILL.md; (3) a benchmark
methodology for objective skill evaluation; (4) a catalog of peripheral-level
capabilities to assess against Axiom's gap list. Implementation must be
independently authored and integrated into Axiom's existing skill/agent/rule/
workflow/profile architecture.
