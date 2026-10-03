# ADR-0001: mcu as the Phase 3 template skill

Status: accepted
Date: 2026-10-03
Scope: embedded-skills-deep-update v1.0.0, Phase 3

## Context

47 skills are flat `SKILL.md + manifest.yaml` stubs (Phase 1 audit).
Phase 3 must expand them one branch per skill without monolithic
`skills/<domain>/src` trees (architecture decision: domains live in
`domains/` overlays, composed via `profiles/skill-update-profile.yaml`).

## Decision

Expand `mcu` first as the structural template, then replicate to
`rtos` → `autosar` → `safety` → `embedded-linux` → `edge-ai` → `robotics`
→ remaining skills. Template sections: Objectives, Prerequisites,
Outcomes, Time estimate, Resources (with source URLs), selection guide,
protection/security, startup/linker/clock, drivers/HAL, build, RTOS
choice, test strategy, traceability, compliance mapping, verification
checklist.

## Standards pinned by Phase 2 research

- MISRA C:2025 (latest, Mar 2025) over 2023 baseline; MISRA C++:2023 (C++17).
- Arm Cortex-M comparison (M0–M7, TrustZone, MPU, DSP/FPU).
- CMake >= 3.20 baseline (LLVM/Clang floor).
- FreeRTOS 202604 LTS (to 2028-04-30); Zephyr LTS; Yocto 6.0 Wrynose LTS.
- ISO 26262:2018 current (Ed.3 DIS, not citable); DO-178C + DO-330/331/332/333.

## Consequences

- Positive: consistent structure, cited claims, per-skill branches stay small.
- Negative: 46 skills still pending; re-audit required after each wave.
- Follow-up: ADR per safety/security-sensitive skill before its PR.
