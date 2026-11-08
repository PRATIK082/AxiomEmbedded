---
name: axiom-framework-esp-idf
title: ESP-IDF Framework Engineering
description: >
  Engineering guide for ESP-IDF projects: component model, CMake build, FreeRTOS tasks, HAL and drivers, GPIO/UART/SPI/I2C, NVS, partition tables, OTA, logging, debugging with JTAG/OpenOCD, build/flash/monitor, memory, power management, and security (secure boot and flash encryption). Hardware-aware: target and pin constraints.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, soc]
axiom:
  dotted_name: axiom.platform.framework.esp_idf
  domain: platform
  subdomain: esp-idf
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [framework, esp-idf, esp32]
  related_skills: [axiom-hardware-aware-checks, axiom-embedded-firmware-bringup]
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [component, CMake project, partition table, OTA plan, debug notes]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints, target profile]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom ESP-IDF Framework Engineering

## Purpose
Provide engineering guidance for projects built on ESP-IDF: how the component model and CMake build work, how to structure FreeRTOS tasks, use HAL/drivers and peripherals (GPIO, UART, SPI, I2C), manage NVS and partition tables, implement OTA, use logging, debug with JTAG/OpenOCD, build/flash/monitor, manage memory and power, and apply security features (secure boot, flash encryption). The skill is hardware-aware: target selection and pin constraints are checked before code generation.

Scope: framework engineering (platform). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- An ESP32/ESP32-S/C/H target has been selected and the project needs structured engineering guidance.
- Reviewing or refactoring an ESP-IDF project for build, task, or memory issues.
- Implementing OTA, NVS, or security features.
- Setting up reproducible build/flash/monitor workflows.

## When Not to Use
- As a substitute for safety certification or qualified security review.
- For targets not supported by ESP-IDF.
- When a different RTOS or framework is mandated by the product requirements.

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Target profile: chip variant, module, flash size, PSRAM, pin capabilities.
- Intended peripherals and interfaces.

## Optional Inputs
- Existing components, CMake files, partition tables.
- SDK configuration (sdkconfig) notes.
- Performance, memory, and power budgets.

## Prerequisites
- `axiom doctor --skip-tests` green.
- ESP-IDF installed and environment sourced.
- Hardware profile declared (see axiom-hardware-aware-checks).

## Execution Workflow
1. Normalize request: objective, scope, constraints, target profile.
2. Inspect repository context and existing ESP-IDF artifacts.
3. Validate target and pin constraints against the hardware profile.
4. Select component structure and CMake layout.
5. Implement tasks, drivers, storage, and OTA with resource and timing rules.
6. Build, flash, and monitor; capture output.
7. Debug using logs and JTAG/OpenOCD when available.
8. Validate structurally and semantically.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Target and flash/PSRAM profile must be declared and match hardware.
- Pin mapping must be verified against the chip datasheet and board.
- Task priorities and stack sizes must be justified and tested.
- NVS keys and namespaces must be documented and versioned.
- Partition table must fit flash and include OTA slots when OTA is used.
- Security features must be enabled deliberately and tested on hardware.
- Blocking calls must not run in high-priority tasks without bounds.

## Workflow
Follow Execution Workflow. Record target, components, task table, partition table, build/flash commands, and debug method in the run manifest.

## Deliverables
- Component structure and CMake files.
- `target-profile.md` (chip, flash, PSRAM, pins).
- `task-table.md` (tasks, priorities, stacks, owners).
- `partition-table.md` (partitions and OTA slots).
- `build-flash-monitor.md` (commands and versions).
- Run manifest under `.axiom/runs/<timestamp>/axiom-framework-esp-idf/`.

## Acceptance Criteria
- Target and pin map declared and conflict-free.
- Build succeeds and warnings reviewed.
- Task stacks and priorities documented and tested.
- Partition table valid for declared flash.
- Human review for security-relevant output.

## Acceptance
- Machine gates: checklist green; validation script passes.
- Human gate: reviewer sign-off for release use.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-framework-esp-idf`.
2. Review checklist gates in `checklists/review.yaml`.
3. Run `idf.py build` for the target.
4. Human review for high-risk levels.

## Common Failure Modes
- Wrong target selected -> binary and pin map wrong; verify `idf.py set-target`.
- Stack overflow in task -> increase stack or reduce work; use uxTaskGetStackHighWaterMark.
- NVS namespace mismatch -> document and version keys.
- Partition table too large for flash -> recalc and test OTA.
- Flash encryption enabled without recovery plan -> document and test.
- Watchdog reset due to blocking work -> yield or move work to lower priority.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not store production secrets in source; use secure storage and build gating.

## Component Model
- Components are reusable units with CMakeLists.txt and public headers.
- Dependencies declared in CMake and component.yml.
- Keep components small and cohesive; avoid circular dependencies.

## CMake Build
- Use `idf.py` as the primary build entry point.
- Keep project-level CMake minimal; delegate to components.
- Pin ESP-IDF version and toolchain.
- Store build commands in scripts for reproducibility.

## FreeRTOS Tasks
- Define task priority, stack size, and core affinity explicitly.
- Keep ISRs and high-priority tasks short.
- Use queues and event groups for inter-task communication.
- Monitor stack high-water marks during testing.

## HAL and Drivers
- Prefer ESP-IDF driver APIs over direct register access.
- Initialize peripherals with explicit configuration structs.
- Check return codes and handle errors.
- Document pin and resource ownership.

## GPIO, UART, SPI, I2C
- Configure pins with mode, pull, and drive strength.
- Set baud rates and timeouts explicitly.
- Use DMA for high-throughput transfers where available.
- Verify bus timing with a scope or analyzer.

## NVS
- Use namespaces and documented keys.
- Version the schema and handle migration.
- Protect sensitive data with encryption where supported.
- Test wear and power-loss scenarios.

## Partition Table
- Define partitions for app, OTA, NVS, and storage.
- Ensure OTA slots are equal size.
- Validate against flash size and chip constraints.
- Keep a recovery path for failed updates.

## OTA
- Use a robust update protocol with rollback.
- Verify image signatures and versions.
- Test power loss and interruption.
- Document rollback and recovery procedures.

## Logging
- Use ESP_LOG with levels and tags.
- Gate verbose logs behind build configuration.
- Avoid logging secrets or personal data.
- Capture logs during testing for evidence.

## Debugging (JTAG/OpenOCD)
- Use OpenOCD with the appropriate adapter.
- Enable JTAG pins and avoid conflicts with application use.
- Use GDB for breakpoints and backtraces.
- Capture core dumps for post-mortem analysis.

## Build, Flash, Monitor
- Build with `idf.py build`.
- Flash with `idf.py flash` and monitor with `idf.py monitor`.
- Use `idf.py fullclean` when configuration changes.
- Record versions and commands in the run manifest.

## Memory
- Track heap, stack, and DMA-capable memory.
- Use PSRAM deliberately and test availability.
- Avoid fragmentation; prefer static allocation for critical paths.
- Monitor memory under load.

## Power Management
- Configure light/deep sleep and wake sources explicitly.
- Measure current at each mode.
- Test wake latency and peripheral state retention.
- Document power budget and margins.

## Security (Secure Boot and Flash Encryption)
- Enable secure boot and verify keys are protected.
- Enable flash encryption and test recovery.
- Store keys securely; never commit private keys.
- Validate the secure boot chain on hardware.

## Hardware-Aware Notes
- Target selection: match chip, flash, PSRAM, and peripherals.
- Pin constraints: respect strapping pins and reserved functions.
- External components: verify voltage and bus compatibility.

## References
- ESP-IDF documentation (landing: https://docs.espressif.com/projects/esp-idf/en/latest/).
- FreeRTOS documentation (landing: https://www.freertos.org/Documentation/RTOS_book.html).
- OpenOCD documentation (landing: https://openocd.org/doc/).
---

Manifest and checklist.<|end|><|start|>startup to=assistant<|channel|>analysis <|constrain|>xml<|message|><rfl:parameter name="path">
E:/My_Project/My_Github/AxiomEmbedded/skills/axiom-framework-esp-idf/manifest.yaml