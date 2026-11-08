---
name: axiom-storage-and-memory
title: Non-Volatile Storage and Memory Engineering
description: >
  Engineers non-volatile storage: internal flash, EEPROM/emulated EEPROM, external SPI NOR flash,
  SD cards, wear leveling, power-fail safety, atomic writes, file systems (FAT/LittleFS),
  endurance and verification.
version: 1.2.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.storage.memory
  domain: platform
  subdomain: storage
  category: implementation
  maturity: experimental
  owner: axiom-embedded
  tags: [storage, flash, eeprom, filesystem, wear-leveling]
  related_skills:
  - bootloader
  - drivers
  - hardware-bringup
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [storage architecture, endurance test plan, data-integrity report]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
  checklists:
  - checklists/review.yaml
---

# Axiom Non-Volatile Storage and Memory Engineering

## Purpose
Engineers non-volatile storage and memory subsystems with power-fail safety, bounded wear, atomic updates,
and verified endurance. This skill is original AxiomEmbedded content.

Scope: storage (platform). Maturity: experimental.

## When to Use
- The project needs flash/EEPROM/external flash/SD/file-system design or verification.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Storage media datasheets, endurance ratings, and power-fail requirements.

## Optional Inputs
- Existing storage drivers, file-system configs, wear-leveling notes, prior test reports.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded (`bootloader`, `drivers`, `hardware-bringup`).

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing storage artifacts.
3. Select media and file system per requirements.
4. Generate or modify artifacts (dry-run first).
5. Validate structurally and semantically (scripts/ + checklists/).
6. Run applicable checks; record results.
7. Produce traceability and review evidence.
8. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer explicit configuration over invented defaults; flag every assumption.
- Safety/security-relevant outputs require human review (review_required: true).

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Storage media selection
- **Internal flash**: fast, no extra BOM, but erase granularity (sector/page) and limited endurance (10k-100k cycles).
- **EEPROM/emulated EEPROM**: byte-level writes, moderate endurance; emulate in flash with wear leveling when no native EEPROM.
- **External SPI NOR**: large capacity, off-chip; account for SPI throughput, CS timing, and power-fail windows.
- **SD card/eMMC**: removable, high capacity; variable latency and vendor behavior; not for hard real-time writes.
- Match media to write frequency, retention, temperature range, and cost.

## Write strategy and atomicity
- Never update in place for critical records; use write-new-then-commit (double buffer / ping-pong).
- Include magic number, version, length, CRC/checksum, and sequence counter in every record.
- Commit only after full payload + CRC are written and verified; use a commit flag or atomic pointer swap.
- Align writes to media page size; pad and handle partial-page writes explicitly.
- Provide rollback on corrupt/old record; never leave storage in an ambiguous state.

## Power-fail safety
- Identify the longest non-atomic operation and worst-case power-loss window.
- Use brown-out detection/reset to prevent writes during voltage collapse.
- Keep critical writes short; disable interrupts only for the minimal commit window.
- Test power-cut at every byte offset of a write cycle (power-fail injection).
- Validate recovery after truncated writes, torn pages, and repeated resets.

## Wear leveling and endurance
- Track erase counts per block; distribute writes across the pool.
- Reserve spare blocks for remapping; plan for graceful degradation near end of life.
- Separate high-churn (logs, counters) from low-churn (config) regions.
- Compute required endurance from write rate x lifetime x safety factor; compare to media rating.
- Run accelerated endurance tests and record cycles-to-failure distribution.

## File systems
- **FAT/exFAT**: interoperable, but not power-fail safe by default; use with caution for critical data.
- **LittleFS**: designed for flash, power-fail safe, wear leveling; preferred for embedded.
- Mount read-only when possible; fsync/sync critical files explicitly.
- Handle full-storage and corrupt-superblock cases with defined recovery.
- Keep file-system metadata and application records versioned and migratable.

## Verification
- Power-cut injection across write boundaries with automated reset.
- CRC/integrity checks on boot; quarantine corrupt records.
- Endurance cycling with erase-count logging and failure analysis.
- Performance (throughput/latency) under worst-case file-system state.
- Cross-temperature retention and read-disturb checks where applicable.

## Deliverables
- Storage architecture (media, layout, record format, wear policy).
- Endurance and data-integrity test plan with evidence.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-storage-and-memory`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `bootloader`, `drivers`, `hardware-bringup`.
