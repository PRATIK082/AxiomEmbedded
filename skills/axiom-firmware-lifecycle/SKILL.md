---
name: axiom-firmware-lifecycle
title: Firmware Lifecycle and Target Management
description: >
  Standardizes building, signing, flashing (via OpenOCD, J-Link, DFU, or
  U-Boot/TFTP), and resetting targets across silicon vendors, with binary hash
  recording and reproducible build discipline. Produces the trusted firmware
  identity (hash plus build provenance) that pre-check phases gate on before
  any test executes. Use when any campaign must flash, reset, or attest the
  firmware on a physical or virtual target.
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.validation.firmware_lifecycle
  domain: all
  maturity: experimental
  safety_critical: false
  activity: implementation
  capability_kind: platform
  primary_domain: all
  risk_class: medium
  inputs: [source tree, toolchain profile, target definition, signing policy]
  outputs: [firmware binary, binary hash, flash report, run manifest]
  required_tools: [run_skill]
  optional_tools: [validate_skill]
  lifecycle: [plan, implement, verify, evidence]
  standards: []
  artifact_types: [firmware binary, flash report, evidence package]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  related_skills: []
---
# Firmware Lifecycle and Target Management

## Purpose

Own the path from source to running target: reproducible builds, image
signing, flashing across vendor toolchains (OpenOCD, J-Link, DFU, U-Boot/TFTP),
and deterministic reset. Every flashed image is attested by hash plus build
provenance; the pre-check phase of any campaign gates on this identity before
executing a single test.

## When to Use

- A campaign must build, flash, reset, or attest firmware on any target.
- A new silicon vendor or board needs a standard flash/reset path.
- Inputs below are available.

## When Not to Use

- As a substitute for qualified safety/security certification review.
- When the toolchain or target definition is absent (record the gap).

## Required Inputs

- Source tree and toolchain profile (compiler, flags, lockfile).
- Target definition (silicon, board, probe, interface, logical names).
- Signing policy (required keys, allowed bypasses, approver).

## Optional Inputs

- Prior flash reports, known-good hashes, factory image backups.

## Prerequisites

- `axiom doctor --skip-tests` green.
- Probe drivers installed; target reachable via the declared interface.

## Execution Workflow

1. Normalize the request into build target, image kind, and flash path.
2. Clean reproducible build; record compiler, flags, commit, and binary hash.
3. Sign per policy (or record an approved bypass with owner and expiry).
4. Pre-flash pre-check: probe reachable, target voltage present, image hash logged.
5. Flash via the vendor path (OpenOCD, J-Link, DFU, U-Boot/TFTP); verify by read-back.
6. Deterministic reset to a known state; capture boot log.
7. Validate structurally (scripts/ plus checklists/).
8. Summarize assumptions, risks, next actions.

## Decision Rules

- Reproducible builds only: same source plus same toolchain equals same hash.
- Read-back verification after every flash; a flash without verify is a failure.
- Signing bypasses require an owner and an expiry; silent bypasses are rejected.
- Prefer explicit configuration over invented defaults; flag every assumption.

## Tool Invocations

- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.

## Workflow

Follow Execution Workflow; record per-step evidence in the run manifest.

## Vendor Paths

| Target class | Build | Flash | Reset |
|---|---|---|---|
| Cortex-M via debug probe | arm-none-eabi-gcc | OpenOCD or J-Link | probe reset plus boot-log capture |
| DFU-capable MCU | arm-none-eabi-gcc | DFU-util over USB | USB re-enumeration check |
| Embedded Linux (MPUs) | yocto/buildroot or distro | U-Boot/TFTP or SD image | power-cycle via relay plus boot prompt |

## Deliverables

- Firmware binary with hash and build provenance, flash report with
  read-back evidence, boot log.

## Acceptance Criteria

- `validate_skill` passes; checklist gates all green; traceability complete.
- Binary hash recorded and matches the pre-check gate value downstream.
- Read-back verification evidence present for every flash.

## Acceptance

- All checklist gates pass; findings carry severity plus evidence plus action.

## Validation Procedure

1. `python skills/axiom-firmware-lifecycle/scripts/validate.py`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes

- Flashing without read-back verification -> reject at review.
- Toolchain drift producing a new hash from unchanged source -> lock the toolchain.
- Unsigned production image without approved bypass -> block the campaign.

## Guardrails

- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## Secure Boot Verification

Where the target implements secure boot (for example MCUboot or wolfBoot
class loaders), the campaign verifies the chain rather than assuming it:
signature verification succeeds for the attested image, version
anti-rollback rejects a downgraded image, the recovery image is present and
addressable, and debug ports sit in the production lock state. Any bypass
fused or jumpered for development is recorded as a finding with owner and
expiry; a silent bypass blocks the campaign.

## Update-Fault Validation

Firmware update paths are fault-injected before they are trusted: corrupt,
truncated, and wrong-key images must be rejected without bricking; power cut
during write must recover to a known-good slot (A/B discipline) with the
recovery evidenced by boot log plus version query. Storage, CPU, bus, and
OTP fault classes map to expected recovery states declared in advance; each
pair carries a security postcondition (no unsigned code executes, no secret
leaks into logs).

## Third-Party CVE Correlation

Inventory every third-party firmware component (RTOS, network stack,
crypto library, SDK blobs) with version pins, match against known CVE
feeds available to the project, and triage into blocker, major, or minor
buckets with the same determinism as static-analysis triage. Unpinned or
unknown-version components are findings, not passes.

## On-Target Test Invocation

Unit suites built for the host also run on target where the runner supports
it (pytest-embedded class flows): flash the test firmware, execute over the
console channel, collect results back into the same report format. Host and
target verdicts are recorded separately; divergence is a finding about the
hardware abstraction, never averaged away.

## Boundary End-Caps

- Lower end-cap: no flash without a reproducible build (source plus
  toolchain pinned, hash recorded) and a declared signing policy.
- Upper end-cap: flash report carries binary hash, read-back evidence, boot
  log, and provenance; downstream pre-checks gate on the hash.
- Out of scope: key ceremony management, HSM operations, and production
  line provisioning (policies are inputs; custody stays with the owner).

## Advanced V&V patterns (P1)

### Flash caching `[MEDIUM]`
Hash-based skip-reflash when the attested image is already present; invalidate
on hash mismatch or policy change.

### Panic/core-dump decoding `[HIGH]`
Automated backtrace decode on boot failure or crash; attach decoded trace to
the flash report and defect.

### Cloud emulation `[MEDIUM]`
QEMU encrypted-flash simulation for secure-boot and update-path validation
before hardware availability; promotion to physical target remains mandatory.

### Firmware provisioning in CI `[HIGH]`
Automated flash of attested firmware in CI before test stages; hash gated in
pre-check.

### Secure boot validation `[CRITICAL]`
eFuse timing checks, encrypted-flash simulation, voltage-glitch fault
injection against the secure-boot path; verify anti-rollback and recovery.

## Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| FW-R1 | ISO 26262-6 Cl. 9 | Software verification incl. update paths |
| FW-R2 | NIST SP 800-193 | Platform firmware resiliency |

## References

- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `axiom-validation-orchestrator`, `axiom-hw-interface-control`,
  `axiom-sil-hil-bridge`, `axiom-validation-levels`.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| firmware-reproducible-build | Project rule (no external standard cited) | HIGH |
| firmware-readback-verify | Project rule (no external standard cited) | CRITICAL |
| firmware-signing-policy | Project rule (no external standard cited) | CRITICAL |
| firmware-hash-attestation | Project rule (no external standard cited) | HIGH |
| firmware-deterministic-reset | Project rule (no external standard cited) | MEDIUM |
| firmware-update-fault-injection | Project rule (no external standard cited) | HIGH |
| firmware-cve-correlation | Project rule (no external standard cited) | MEDIUM |

## Impact tiers

| Impact tier | Meaning | Typical handling |
|---|---|---|
| CRITICAL | Safety/security-critical; release blocker; core/evidence zone | Human approval required; no autonomous AI action |
| HIGH | Major correctness or compliance impact | Reviewed change; evidence required |
| MEDIUM | Moderate impact | Standard review |
| LOW | Minor or advisory | Batched review acceptable |

### Rule impact assignments

| Rule ID | Impact tier |
|---|---|
| firmware-reproducible-build | HIGH |
| firmware-readback-verify | CRITICAL |
| firmware-signing-policy | CRITICAL |
| firmware-hash-attestation | HIGH |
| firmware-deterministic-reset | MEDIUM |
| firmware-update-fault-injection | HIGH |
| firmware-cve-correlation | MEDIUM |

## Deviation management

Any deviation from a rule or standard in this skill must be recorded as a
first-class artifact (not a code comment) with all of the following:

- Rule ID
- Reason
- File / location
- Approver
- Date

Deviations against CRITICAL rules require a safety/security lead approval and
an impact assessment. Store deviation records under the project evidence or
change-control location and link them in the traceability matrix.

## Builder + reviewer pairing

Where this skill produces an artifact, pair it with an independent confirmation review before acceptance; reviewers do not modify the artifact. No single dedicated reviewer skill is assigned in the catalog for this legacy skill, so use the domain review skill or a human reviewer.

## Three-zone autonomy

Autonomy is zoned by risk; the V&V boundary is the automation boundary.

- Core / evidence zone (AI no access, human accountable): certified or
  qualified artifacts, evidence records, safety/security-critical code, and
  release baselines. AI must not read or write here without an explicit
  human-approved change request.
- Gray zone (AI assistant + HITL): AI plans and drafts; a human decides and
  approves each step. Architecture, requirements, tests with safety impact, and
  verification-affecting configuration live here.
- Non-critical zone (AI unrestricted): documentation, examples, scaffolding,
  low-risk refactors, and tooling glue.

This skill's outputs are treated as gray-zone by default; AI may draft but a
human approves. AI must never act autonomously in the core/evidence zone.
