---
name: bootloader
description: >
  Verify-before-jump boot, A/B slots, anti-rollback, key custody. Use when
  building secure updateable bootloaders.
version: 1.2.0
domains: [all]
platforms: [mcu, mpu, soc]

axiom:
  dotted_name: axiom.legacy.bootloader
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: [axiom-embedded-firmware-bringup]
  checklists: [checklists/bootloader-checklist.md]

  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: []
  optional_tools: []
---
# Bootloader skill

First-stage and update-capable bootloaders for MCU/MPU targets: verified boot
chains, in-field update with atomic switch and rollback, and recovery paths
that survive power loss at any instant.

## 1. Purpose and scope

**Purpose.** Own the first code that runs: hardware init, image verification,
and a fail-safe update mechanism so no released device can be bricked from
software.

**In scope.** ROM/FSBL/SSBL staging, image formats and slots (A/B, trial/
permanent), signature verification, anti-rollback, recovery/UART-USB fallback,
watchdog-guarded boot, and update-agent protocol design.

**Non-goals.** Application firmware (see `bare-metal`, `mcu`) and server-side
OTA fleet management. Ends at a verified jump to the application with the
update story proven on hardware.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | NIST SP 800-193 Platform Firmware Resiliency | Rev. 1 (2024) | Protection, detection, recovery of platform firmware | `https://csrc.nist.gov/pubs/sp/800/193/r1/final` |
| 2 | U-Boot verified boot | Current (FIT signatures, dm-verity root) | Reference verified-boot implementation for MPU stages | `https://docs.u-boot.org/en/latest/usage/secure_boot.html` |
| 3 | MCUboot | Current (Apache 2.0 OSS bootloader) | Image slots, swap modes, signed update reference design | `https://docs.mcuboot.com/` |

## 3. Boot chain rules

1. **Verify before jump.** Every stage verifies the next (hash at minimum,
   signature where keys exist) before transferring control. The application
   vector table and entry are sanity-checked (range, alignment, stack pointer
   in RAM) -- a corrupt image never gets control.
2. **Watchdog from reset.** Independent watchdog armed before any
   unbounded wait (flash erase, UART autobaud, USB enumeration); a hung
   bootloader resets into a known state instead of hanging the line.
3. **Recovery always reachable.** A hardware-forced recovery path (button
   combo, double-tap reset into UF2/DFU/UART loader) exists that no software
   update can erase -- ROM-based where the silicon offers it.

## 4. Update protocol

1. **Atomic switch.** A/B slots or MCUboot-style swap/scratch with a
   confirmation step: new image boots as *trial*, runs self-test, then marks
   *permanent*. Power loss at any point leaves a bootable image.
2. **Anti-rollback.** Monotonic version counter in protected storage rejects
   older images; downgrade attacks fail closed with an auditable event.
3. **Transport integrity.** Update images carry signatures end-to-end (server
   to bootloader); transport checksums (CRC) catch corruption, signatures
   catch malice -- both, always.
4. **Power-loss testing.** The release campaign cuts power at every phase
   (download, verify, swap, confirm) on hardware; each case boots to a
   working image. Untested phases are release blockers.

## 5. Key management posture

Production signing keys live offline (HSM or equivalent); the bootloader ships
only public keys in protected flash. Key rotation and revocation procedure is
documented before first production signing -- a leaked-key drill the team has
run, not a paragraph written during the incident.

## 6. Release gates (blocking)

1. Verify-before-jump on every stage with entry sanity checks.
2. Trial/permanent slot discipline with self-test confirmation.
3. Anti-rollback enforced and tested with a real downgrade attempt.
4. Recovery path demonstrated from a deliberately corrupted application.
5. Power-loss matrix green on hardware (S4.4).
6. Key custody and rotation procedure documented and drilled.

## 7. Verification of this skill (Phase 4 gate)

- No update path can brick: proven by test (S4.4, S6.4), not by argument.
- Keys and trust anchors reviewed per `security` policy.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| bootloader-verify-before-jump | NIST SP 800-193 Rev. 1 (protection) | CRITICAL |
| bootloader-watchdog-from-reset | NIST SP 800-193 Rev. 1 (protection) | HIGH |
| bootloader-recovery-reachable | NIST SP 800-193 Rev. 1 (recovery) | CRITICAL |
| bootloader-atomic-switch | NIST SP 800-193 Rev. 1 (recovery) | CRITICAL |
| bootloader-anti-rollback | NIST SP 800-193 Rev. 1 (protection) | CRITICAL |
| bootloader-transport-integrity | NIST SP 800-193 Rev. 1 (protection) | HIGH |
| bootloader-power-loss-testing | NIST SP 800-193 Rev. 1 (detection/recovery) | HIGH |
| bootloader-key-custody | NIST SP 800-193 Rev. 1 (protection) | CRITICAL |

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
| bootloader-verify-before-jump | CRITICAL |
| bootloader-watchdog-from-reset | HIGH |
| bootloader-recovery-reachable | CRITICAL |
| bootloader-atomic-switch | CRITICAL |
| bootloader-anti-rollback | CRITICAL |
| bootloader-transport-integrity | HIGH |
| bootloader-power-loss-testing | HIGH |
| bootloader-key-custody | CRITICAL |

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

## Workflow

Follow the lifecycle and verification steps in this skill; record evidence per the applicable schema.

## Acceptance

All applicable release gates in this skill are satisfied and recorded with human approval where required.
