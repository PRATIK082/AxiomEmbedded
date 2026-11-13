---
name: axiom-framework-zephyr
title: Zephyr RTOS Framework Engineering
description: >
  Engineering guide for Zephyr RTOS projects: devicetree, Kconfig, west build
  and flash, drivers API, workqueues, threads, power management, logging, shell,
  testing with ztest, and portability across boards. Hardware-aware: board
  definitions and pin constraints. Use when framework zephyr tasks arise in all
  projects.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu, soc]

axiom:
  dotted_name: axiom.platform.framework.zephyr
  domain: platform
  subdomain: zephyr
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [framework, zephyr, rtos]

  related_skills: [axiom-hardware-aware-checks, axiom-embedded-firmware-bringup]

  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [devicetree overlay, Kconfig, west project, driver, test suite]
  mcp_tools: [run_skill, validate_skill]

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints, board profile]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---
# Axiom Zephyr RTOS Framework Engineering

## Purpose
Provide engineering guidance for projects built on Zephyr RTOS: how to use devicetree and Kconfig, build and flash with west, use the drivers API, workqueues and threads, manage power, use logging and shell, test with ztest, and maintain portability across boards. The skill is hardware-aware: board definitions and pin constraints are checked before code generation.

Scope: framework engineering (platform). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- A Zephyr-supported board has been selected and the project needs structured engineering guidance.
- Reviewing or refactoring a Zephyr project for build, device, or resource issues.
- Implementing drivers, overlays, or power management.
- Setting up reproducible west builds and ztest suites.

## When Not to Use
- As a substitute for safety certification or qualified security review.
- For boards without Zephyr support unless adding a board port is in scope.
- When a different RTOS or framework is mandated by the product requirements.

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Board profile: board name, SoC, flash/RAM, pin capabilities.
- Intended peripherals and interfaces.

## Optional Inputs
- Existing overlays, Kconfig fragments, driver code.
- West manifest and module notes.
- Performance, memory, and power budgets.

## Prerequisites
- `axiom doctor --skip-tests` green.
- Zephyr SDK and west installed.
- Hardware profile declared (see axiom-hardware-aware-checks).

## Execution Workflow
1. Normalize request: objective, scope, constraints, board profile.
2. Inspect repository context and existing Zephyr artifacts.
3. Validate board and pin constraints against the hardware profile.
4. Select devicetree overlay and Kconfig configuration.
5. Implement drivers, threads, workqueues, and power management.
6. Build and flash with west; capture output.
7. Test with ztest and shell where applicable.
8. Validate structurally and semantically.
9. Produce traceability and review evidence.
10. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Board must be a supported Zephyr board or a documented custom port.
- Devicetree changes must be in overlays, not core board files, unless porting.
- Kconfig must be minimal and documented.
- Thread priorities and stack sizes must be justified and tested.
- Drivers must use the Zephyr driver API and devicetree binding.
- Power management must be tested on hardware.
- Tests must run in CI or on target with recorded results.

## Workflow
Follow Execution Workflow. Record board, overlay, Kconfig, thread table, build/flash commands, and test results in the run manifest.

## Deliverables
- Devicetree overlay and Kconfig fragments.
- `board-profile.md` (board, SoC, pins, capabilities).
- `thread-table.md` (threads, priorities, stacks).
- `build-flash.md` (west commands and versions).
- `test-report.md` (ztest results).
- Run manifest under `.axiom/runs/<timestamp>/axiom-framework-zephyr/`.

## Acceptance Criteria
- Board and pin map declared and conflict-free.
- Build succeeds and warnings reviewed.
- Thread stacks and priorities documented and tested.
- ztest suite passes on target or emulation.
- Human review for safety/security-relevant output.

## Acceptance
- Machine gates: checklist green; validation script passes.
- Human gate: reviewer sign-off for release use.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-framework-zephyr`.
2. Review checklist gates in `checklists/review.yaml`.
3. Run `west build` for the target board.
4. Run `west flash` and ztest as applicable.
5. Human review for high-risk levels.

## Common Failure Modes
- Board not supported -> add a board port or choose supported board.
- Overlay not applied -> check CMake and board name.
- Kconfig missing -> feature silently disabled; audit configuration.
- Thread stack overflow -> use larger stack or reduce work; monitor usage.
- Driver binding mismatch -> verify compatible string and status.
- Power management breaks peripherals -> test wake and state retention.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.
- Do not modify core Zephyr tree; keep changes in application or module.

## Devicetree
- Use overlays to configure peripherals and pins.
- Keep board-specific changes in overlays, not source.
- Verify bindings and compatible strings.
- Document node labels and usage.

## Kconfig
- Enable only required features to save memory.
- Use fragments for reusable configuration.
- Document non-default options.
- Audit for hidden dependencies.

## West Build and Flash
- Use `west build -b <board>` and `west flash`.
- Pin Zephyr version via west manifest.
- Use `west update` for modules.
- Store commands in scripts for reproducibility.

## Drivers API
- Use device_get_binding or DEVICE_DT_GET.
- Check device readiness before use.
- Use async APIs where available.
- Handle errors and timeouts.

## Workqueues
- Use system workqueue for short tasks.
- Create dedicated workqueues for blocking work.
- Avoid heavy work in ISR context.
- Document work item ownership.

## Threads
- Define priority, stack size, and entry point explicitly.
- Use mutexes and semaphores for synchronization.
- Avoid priority inversion; use priority inheritance where needed.
- Monitor stack usage during testing.

## Power Management
- Enable PM subsystem and configure states.
- Test sleep and wake with peripherals.
- Measure current and wake latency.
- Document power budget and margins.

## Logging
- Use LOG_MODULE_REGISTER and levels.
- Gate verbose logs behind configuration.
- Avoid logging secrets.
- Capture logs for evidence.

## Shell
- Enable shell for interactive debugging.
- Register commands with clear help text.
- Gate shell in production builds.
- Avoid exposing unsafe commands.

## Testing (ztest)
- Write unit and integration tests with ztest.
- Run tests on target or emulation.
- Record results and failures.
- Include tests in CI where possible.

## Portability Across Boards
- Keep board-specific code in overlays and Kconfig.
- Test on at least two boards when feasible.
- Avoid hardcoded pins or addresses.
- Document supported boards.

## Board Definitions
- Use supported boards from Zephyr tree.
- For custom boards, follow the board porting guide.
- Keep custom board files in a separate directory or module.
- Document board capabilities and limitations.

## Hardware-Aware Notes
- Board selection: match SoC, flash, RAM, and peripherals.
- Pin constraints: respect reserved pins and strapping.
- External components: verify voltage and bus compatibility.

## References
- Zephyr documentation (landing: https://docs.zephyrproject.org/latest/).
- Zephyr west documentation (landing: https://docs.zephyrproject.org/latest/develop/west/index.html).
- Zephyr testing documentation (landing: https://docs.zephyrproject.org/latest/develop/test/index.html).
---

Manifest and checklist.<|end|><|start|>startup to=assistant<|channel|>analysis <|constrain|>xml<|message|><rfl:parameter name="path">
E:/My_Project/My_Github/AxiomEmbedded/skills/axiom-framework-zephyr/manifest.yaml