---
name: security
description: Threat modeling, secure boot, crypto inventory, fuzzing, SBOM/CVE watch. Use when hardening products or answering security requirements.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Security skill

Product security for connected embedded systems: threat modeling, secure boot
and update, cryptography selection, hardening, vulnerability management, and
the evidence that supports UNECE R155/R156, IEC 62443, and SESIP-style claims.

## 1. Purpose and scope

**Purpose.** Ship devices that resist realistic attackers: authenticated boot,
signed updates, least-privilege runtime, and a monitored vulnerability posture
from first customer ship through end of support.

**In scope.** Threat modeling (STRIDE per interface), secure-element/TEE use,
secure boot chains (with `bootloader`, `embedded-linux` §6), cryptography
selection and key lifecycle, hardening baselines, SBOM/CVE monitoring, incident
response and coordinated disclosure.

**Non-goals.** Functional safety (see `safety` — coordinate, don't conflate)
and cloud-backend security beyond the device interface. Ends at a maintained,
monitored device security posture with evidence.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | UNECE R155 / R156 | In force (2021; R155 01-series updates) | Cyber security management and software-update management for vehicles | `https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security` |
| 2 | IEC 62443 | 62443-3-3:2013, 62443-4-1:2018, 62443-4-2:2019 | Industrial automation security: system requirements, secure development, component requirements | `https://www.isa.org/standards-and-publications/isa-standards/isa-standards/isa-iec-62443-series-of-standards` |
| 3 | NIST SP 800-193 | Rev. 1 (2024) | Platform firmware resiliency: protection, detection, recovery | `https://csrc.nist.gov/pubs/sp/800/193/r1/final` |
| 4 | SESIP / PSA Certified | Current assurance methodologies | IoT component security evaluation profiles | `https://www.sesip.levels.io/` |

## 3. Threat modeling rules

1. **Model per interface.** Every external interface (network, BLE, USB,
   debug, OTA, physical) gets STRIDE analysis with trust boundaries drawn;
   unmodeled interfaces are review findings.
2. **Rank by impact × exposure.** Safety-impacting threats coordinate with the
   `safety` HARA; remotely-exploitable + safety-impacting threats top the
   mitigation backlog.
3. **Abuse cases as requirements.** Each accepted threat yields security
   requirements with verification methods (pen test, fuzz, code review) traced
   in the matrix — threats without derived requirements are wishes.

## 4. Technical baseline

1. **Secure boot + signed updates.** Verify-before-jump (`bootloader` §3),
   anti-rollback, offline production keys with rotation drills — no exceptions
   for development variants that can reach customers.
2. **Cryptography.** Named algorithms with parameters (e.g. ECDSA-P256,
   AES-256-GCM, X25519); no custom ciphers, no hardcoded keys, no ECB mode;
   keys in secure storage (secure element/OTP/TEE), unique per device.
3. **Hardening.** Follows `embedded-linux` §7 on Linux targets; on MCU targets:
   readout protection enabled, debug interfaces locked or authenticated,
   unused peripherals clock-gated, stack guards and MPU regions on.
4. **Fuzz the parsers.** Every external-input parser (protocol decoders, image
   parsers, AT/command handlers) runs under a coverage-guided fuzzer in CI
   with a corpus seeded from field captures.

## 5. Lifecycle and disclosure

1. **SBOM + CVE watch.** SPDX SBOM per release (`embedded-linux` §7); automated
   CVE monitoring with SLA-based triage; documented waivers carry expiry dates.
2. **Coordinated disclosure.** Published contact, response SLAs, and a
   patch-delivery path via the OTA mechanism — tested before the first
   incident, not invented during it.
3. **EOL security.** End-of-support date communicated; devices beyond support
   fail safe (function without cloud) and the residual-risk statement is
   recorded.

## 6. Release gates (blocking, human review for safety-adjacent changes)

1. Threat model covers all interfaces with derived, traced requirements.
2. Secure boot + signed update + anti-rollback demonstrated on hardware.
3. Crypto inventory reviewed: algorithms, key storage, per-device uniqueness.
4. Fuzz harnesses green on all external parsers; findings triaged.
5. SBOM generated; CVE posture clean or waiver-documented.
6. Disclosure process published; EOL date recorded.

## 7. Verification of this skill (Phase 4 gate)

- Security claims cite standards with number + version + URL (§2).
- Safety-impacting threats coordinated with `safety`, never siloed (§3.2).
