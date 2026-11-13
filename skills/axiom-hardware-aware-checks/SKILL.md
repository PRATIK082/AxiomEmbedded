---
name: axiom-hardware-aware-checks
title: Hardware-Aware Pre-Generation Checks for Firmware
description: >
  Performs pre-generation checks for firmware projects against a declared
  hardware profile: target MCU/MPU/SoC, board, architecture, peripherals, pin
  assignments, clock configuration, memory, OS, framework, toolchain, external
  components, electrical constraints, interfaces, timing, and debug interfaces.
  Detects pin, peripheral, DMA, and clock conflicts, resource exhaustion,
  unsupported peripherals, invalid framework combinations, voltage and timing
  incompatibility. Never invents missing hardware data; records assumptions and
  open questions. Produces a check report with evidence. Use when hardware aware
  checks tasks arise in all projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu, soc, mpsoc]

axiom:
  dotted_name: axiom.platform.hardware_aware_checks
  domain: platform
  subdomain: hardware-checks
  category: verification
  maturity: experimental
  owner: axiom-embedded
  tags: [hardware, checks, pre-generation]

  related_skills: [hardware-architecture, hardware-bringup, axiom-embedded-firmware-bringup]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [hardware profile, pre-generation check report, assumption log]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs:
  - repository path
  - target files
  - objective
  - constraints
  - hardware profile
  outputs:
  - run report
  - run manifest
  - check report
  required_tools:
  - validate_skill
  optional_tools:
  - run_skill
---
# Axiom Hardware-Aware Pre-Generation Checks

## Purpose
Run a deterministic, evidence-backed set of pre-generation checks before any firmware code or configuration is generated. The skill validates that the declared hardware, software, and toolchain context is internally consistent and sufficient, so generated artifacts do not silently assume pins, clocks, peripherals, memory, or interfaces that the target cannot provide. It never invents missing hardware data; gaps are recorded as assumptions or open questions and block generation until resolved or explicitly accepted.

Scope: pre-generation verification (platform). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- Before generating firmware, drivers, board support, or configuration for a new or changed target.
- When a hardware profile (MCU/MPU/SoC, board, peripherals) has been provided or partially provided.
- When reviewing a generated artifact for hardware plausibility.
- When onboarding a brownfield project and the hardware context must be reconstructed.

## When Not to Use
- As a substitute for hardware validation, bring-up, or qualified safety/security review.
- When no hardware information exists at all and the user refuses to provide any; record the gap instead.
- As proof of electrical or timing compliance; checks are heuristic and require hardware evidence.

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Hardware profile (see `templates/`): target part number and revision, board name/revision, architecture (core, ISA), package, peripherals in use, pin assignments, clock tree, memory map, OS/RTOS, framework, toolchain, external components, interfaces, timing requirements, debug interface.
- If any item is missing, it must be listed as an open question, not guessed.

## Optional Inputs
- Existing schematics, datasheets, errata, board support packages, prior check reports.
- Tool availability and version notes.
- Power and thermal budgets.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills (hardware-architecture, hardware-bringup) loaded.
- A declared hardware profile or an explicit statement that it is unknown.

## Execution Workflow
1. Normalize the request: objective, scope, constraints, and declared hardware profile.
2. Inspect repository context and existing hardware artifacts; collect the declared profile.
3. Build a hardware context table with an explicit status per item: provided, assumed, or unknown.
4. Run conflict checks: pin, peripheral, DMA, clock, resource exhaustion, unsupported peripheral, framework combination, voltage, timing.
5. Record every assumption and open question with owner and required evidence.
6. Generate or modify artifacts only after checks pass or gaps are explicitly accepted.
7. Validate structurally and semantically (scripts/ + checklists/).
8. Produce traceability: requirement -> hardware item -> check -> evidence.
9. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Never invent missing hardware data; mark it unknown and block generation unless the user explicitly accepts the assumption.
- A check with status "unknown input" is a finding, not a pass.
- Conflicts are blocking until resolved or waived with rationale and owner.
- Voltage or timing incompatibility is always blocking.
- Unsupported peripheral on the declared target is blocking unless an alternative is declared.
- Framework combination validity is evaluated against the declared target and OS, not assumed.

## Workflow
Follow Execution Workflow. Each check produces a row: item, expected, observed/declared, status (pass/fail/unknown), severity, evidence, action. Record per-step evidence in the run manifest and the check report.

## Deliverables
- `hardware-context.md` (declared profile with provided/assumed/unknown status).
- `pre-generation-check-report.md` (all checks with severity, evidence, action).
- `assumption-log.md` (assumptions, owners, required evidence, expiry).
- Run manifest under `.axiom/runs/<timestamp>/axiom-hardware-aware-checks/`.

## Acceptance Criteria
- Every hardware context item is classified as provided, assumed, or unknown.
- All conflict checks are executed and recorded.
- No unknown item is silently treated as provided.
- Check report contains severity, evidence, and action for every finding.
- Human review completed for medium or higher risk output.

## Acceptance
- Machine gates: checklist green; validation script passes; no blocking finding unresolved.
- Human gate: reviewer sign-off on assumptions and waivers.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-hardware-aware-checks`.
2. Review checklist gates in `checklists/review.yaml`.
3. Human review for medium/high risk levels and any waiver.

## Common Failure Modes
- Missing pin map invented from a similar board -> record unknown and request schematic/HSI.
- Clock tree assumed from default config -> mark assumed and require measurement.
- DMA conflict missed because channel mapping not declared -> require DMA allocation table.
- Framework chosen without OS compatibility check -> add framework combination check.
- Voltage domain mismatch between MCU and peripheral ignored -> add voltage check row.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not generate code or configuration while blocking findings remain unresolved.

## Hardware Context Items
The following items must be captured or explicitly marked unknown before generation:
- Target MCU/MPU/SoC: part number, revision, core, ISA, package.
- Board: name, revision, schematic reference.
- Architecture: memory map, bus matrix, clock tree, power domains.
- Peripherals: required peripherals and instances.
- Pin assignments: function, direction, alternate function, constraints.
- Clock configuration: sources, PLLs, dividers, peripheral clocks.
- Memory: Flash, RAM, EEPROM/OTP, external memory.
- OS/RTOS: name, version, scheduling model.
- Framework: name, version, supported targets.
- Toolchain: compiler, version, flags, linker script.
- External components: sensors, actuators, transceivers, memory.
- Electrical constraints: voltage domains, current budgets, level shifting.
- Interfaces: UART, SPI, I2C, CAN, Ethernet, USB, etc. with parameters.
- Timing: baud rates, sampling rates, deadlines, jitter.
- Debug interfaces: SWD/JTAG, trace, console UART.

## Check Catalog
- Pin conflicts: same pin assigned to multiple functions or reserved functions.
- Peripheral conflicts: same peripheral instance used by multiple drivers or features.
- DMA conflicts: overlapping channels or incompatible request mapping.
- Clock conflicts: peripheral clock not enabled or source incompatible.
- Resource exhaustion: timer, channel, or memory budget exceeded.
- Unsupported peripherals: peripheral not present on declared target.
- Invalid framework combinations: framework not supporting target/OS/toolchain.
- Voltage incompatibility: IO voltage mismatch between devices.
- Timing incompatibility: requested rate beyond peripheral or bus capability.

## References
- Hardware architecture HSI and bring-up skills in this repository.
- Vendor datasheets, reference manuals, and errata (identifiers + landing URLs only, no normative text).
- IEEE 1149.1 JTAG (landing: https://standards.ieee.org/ieee/1149-1/4244/).
- ARM CoreSight (landing: https://developer.arm.com/documentation/ihi0029/latest/).
---

Let's ensure all sections. Good.

Now manifest and checklist.<|end|><|start|> fileList<|end|>analysis <|constrain|>xml<|message|><rfl:parameter name="path">
E:/My_Project/My_Github/AxiomEmbedded/skills/axiom-hardware-aware-checks/manifest.yaml