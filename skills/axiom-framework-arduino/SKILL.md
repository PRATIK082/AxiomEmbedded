---
name: axiom-framework-arduino
title: Arduino Framework Engineering
description: >
  Engineering guide for Arduino framework projects: core and library model,
  sketch structure, pin mapping, Serial, Wire/SPI, interrupts, timers, memory
  constraints on AVR, portability limits, build via arduino-cli, debugging, and
  safety/security notes. Hardware-aware: board selection and pin constraints.
  Does not assume Arduino is appropriate for all products. Use when framework
  arduino tasks arise in all projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu]

axiom:
  dotted_name: axiom.platform.framework.arduino
  domain: platform
  subdomain: arduino
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [framework, arduino, mcu]

  related_skills: [axiom-hardware-aware-checks, axiom-embedded-firmware-bringup]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [sketch, board profile, build script, debug notes]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs:
  - repository path
  - target files
  - objective
  - constraints
  - board profile
  outputs:
  - run report
  - run manifest
  required_tools:
  - validate_skill
  optional_tools:
  - run_skill
---
# Axiom Arduino Framework Engineering

## Purpose
Provide engineering guidance for projects built on the Arduino framework: how the core and library model works, how to structure sketches, map pins, use Serial/Wire/SPI, handle interrupts and timers, respect AVR memory constraints, and build and debug with arduino-cli. The skill is hardware-aware: board selection and pin constraints are checked before code generation. It explicitly does not assume Arduino is suitable for every product, especially safety-critical or resource-constrained applications.

Scope: framework engineering (platform). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- An Arduino-based board or core has been selected and the project needs structured engineering guidance.
- Porting or reviewing an Arduino sketch for memory, timing, or portability issues.
- Setting up reproducible builds with arduino-cli.
- Evaluating whether Arduino is appropriate for a product.

## When Not to Use
- As a substitute for safety certification or qualified security review.
- For safety-critical products without an approved overlay and qualification plan.
- When the target is not supported by an Arduino core; use a native framework instead.
- When deterministic real-time behavior or certified OS features are required and Arduino cannot provide them.

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Board profile: board name, core, MCU, pin capabilities, voltage, flash/RAM sizes.
- Intended peripherals and interfaces.

## Optional Inputs
- Existing sketches, libraries, and build scripts.
- Toolchain versions and board package versions.
- Performance and memory budgets.

## Prerequisites
- `axiom doctor --skip-tests` green.
- `arduino-cli` installed and board core installed for the target.
- Hardware profile declared (see axiom-hardware-aware-checks).

## Execution Workflow
1. Normalize request: objective, scope, constraints, board profile.
2. Inspect repository context and existing Arduino artifacts.
3. Validate board selection and pin constraints against the hardware profile.
4. Select sketch structure and library dependencies.
5. Implement with memory, timing, and portability rules.
6. Build with arduino-cli and capture output.
7. Debug using serial, LED, and available debug interfaces.
8. Validate structurally and semantically.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Board selection must match the declared hardware profile; do not assume a generic board.
- Pin mapping must be verified against the core variant and board schematic.
- Interrupt service routines must be short and must not call blocking APIs.
- Dynamic memory allocation on AVR must be justified and bounded.
- Library dependencies must be pinned to versions.
- Arduino is not approved for safety-critical use without an overlay and review.
- Portability across cores must be tested, not assumed.

## Workflow
Follow Execution Workflow. Record board, core, pin map, memory budget, build command, and debug method in the run manifest.

## Deliverables
- Sketch structure and source files.
- `board-profile.md` (board, core, pins, capabilities).
- `build.md` (arduino-cli commands and versions).
- `memory-budget.md` (flash/RAM usage and margins).
- Run manifest under `.axiom/runs/<timestamp>/axiom-framework-arduino/`.

## Acceptance Criteria
- Board and core declared and match hardware profile.
- Pin map documented and conflict-free.
- Build succeeds with arduino-cli and warnings reviewed.
- Memory budget within limits with margin.
- Human review for any safety/security-relevant output.

## Acceptance
- Machine gates: checklist green; validation script passes.
- Human gate: reviewer sign-off for release use.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-framework-arduino`.
2. Review checklist gates in `checklists/review.yaml`.
3. Run `arduino-cli compile` for the target board.
4. Human review for high-risk levels.

## Common Failure Modes
- Wrong board selected -> pin map and timings wrong; verify board FQBN.
- Pin conflict with onboard LED/serial -> check variant and schematic.
- ISR too long causing missed interrupts -> move work to main loop.
- Heap fragmentation on AVR -> avoid dynamic allocation or bound it.
- Library version drift -> pin versions in manifest.
- Serial debug left enabled in production -> gate behind build flag.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not assume Arduino suitability for safety-critical products.

## Core and Library Model
- Arduino core provides main(), setup(), loop(), and hardware abstraction.
- Libraries extend functionality; prefer well-maintained, version-pinned libraries.
- Core variant defines pin mapping and available peripherals.
- Avoid direct register access unless documented and portable.

## Sketch Structure
- One primary sketch with setup() and loop().
- Separate modules into .cpp/.h files under src/ when using arduino-cli with a project layout.
- Keep global state explicit and initialized in setup().
- Use configuration headers for board-specific values.

## Pin Mapping
- Use symbolic pin names from the variant; avoid raw numbers where possible.
- Document direction, alternate function, and electrical constraints.
- Verify conflicts with onboard peripherals (LED, USB, serial).

## Serial, Wire, SPI
- Serial for debug and console; define baud rate and timeout.
- Wire (I2C) for sensors; check bus speed and pull-ups.
- SPI for high-speed peripherals; manage chip select and mode.
- Avoid blocking calls in time-critical paths.

## Interrupts and Timers
- Keep ISRs minimal: set flags, capture data, defer processing.
- Disable interrupts only for short critical sections.
- Timer usage must account for PWM and millis()/micros() side effects.
- Document interrupt priorities and nesting.

## Memory Constraints (AVR)
- Flash, SRAM, and EEPROM budgets must be tracked.
- Avoid large static buffers and unbounded recursion.
- Use PROGMEM for constant data where supported.
- Monitor stack usage under worst-case nesting.

## Portability Limits
- APIs differ across cores; test on each target.
- Timing assumptions vary by clock speed.
- Pin capabilities differ; validate per board.
- Avoid core-specific hacks without guards.

## Build via arduino-cli
- Use `arduino-cli core install` and `arduino-cli lib install` with versions.
- Compile with `arduino-cli compile --fqbn <board>`.
- Upload with `arduino-cli upload --fqbn <board> --port <port>`.
- Store commands in a build script for reproducibility.

## Debugging
- Use Serial logging with levels and compile-time gating.
- Use LED patterns for no-serial scenarios.
- Use available debug probes (OpenOCD, JTAG/SWD) where supported.
- Capture golden logs for regression comparison.

## Safety and Security Notes
- Arduino is not for safety-critical use without an approved overlay and qualification.
- Avoid test keys or debug backdoors in production builds.
- Validate inputs and handle faults explicitly.
- Keep watchdog enabled where appropriate.

## Hardware-Aware Notes
- Board selection: match MCU, voltage, pin count, and peripherals to requirements.
- Pin constraints: respect reserved pins and electrical limits.
- External components: verify voltage compatibility and bus loading.

## References
- Arduino documentation (landing: https://www.arduino.cc/reference/en/).
- arduino-cli documentation (landing: https://arduino.github.io/arduino-cli/latest/).
- AVR libc reference (landing: https://www.nongnu.org/avr-libc/).
---

Manifest and checklist.<|end|><|start|>startup to=assistant<|channel|>analysis <|constrain|>xml<|message|><rfl:parameter name="path">
E:/My_Project/My_Github/AxiomEmbedded/skills/axiom-framework-arduino/manifest.yaml