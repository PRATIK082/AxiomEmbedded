---
name: bootloader
description: Verify-before-jump boot, A/B slots, anti-rollback, key custody. Use when building secure updateable bootloaders.
version: 1.2.0
domains: [all]
platforms: [mcu, mpu, soc]
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
   in RAM) — a corrupt image never gets control.
2. **Watchdog from reset.** Independent watchdog armed before any
   unbounded wait (flash erase, UART autobaud, USB enumeration); a hung
   bootloader resets into a known state instead of hanging the line.
3. **Recovery always reachable.** A hardware-forced recovery path (button
   combo, double-tap reset into UF2/DFU/UART loader) exists that no software
   update can erase — ROM-based where the silicon offers it.

## 4. Update protocol

1. **Atomic switch.** A/B slots or MCUboot-style swap/scratch with a
   confirmation step: new image boots as *trial*, runs self-test, then marks
   *permanent*. Power loss at any point leaves a bootable image.
2. **Anti-rollback.** Monotonic version counter in protected storage rejects
   older images; downgrade attacks fail closed with an auditable event.
3. **Transport integrity.** Update images carry signatures end-to-end (server
   to bootloader); transport checksums (CRC) catch corruption, signatures
   catch malice — both, always.
4. **Power-loss testing.** The release campaign cuts power at every phase
   (download, verify, swap, confirm) on hardware; each case boots to a
   working image. Untested phases are release blockers.

## 5. Key management posture

Production signing keys live offline (HSM or equivalent); the bootloader ships
only public keys in protected flash. Key rotation and revocation procedure is
documented before first production signing — a leaked-key drill the team has
run, not a paragraph written during the incident.

## 6. Release gates (blocking)

1. Verify-before-jump on every stage with entry sanity checks.
2. Trial/permanent slot discipline with self-test confirmation.
3. Anti-rollback enforced and tested with a real downgrade attempt.
4. Recovery path demonstrated from a deliberately corrupted application.
5. Power-loss matrix green on hardware (§4.4).
6. Key custody and rotation procedure documented and drilled.

## 7. Verification of this skill (Phase 4 gate)

- No update path can brick: proven by test (§4.4, §6.4), not by argument.
- Keys and trust anchors reviewed per `security` policy.
