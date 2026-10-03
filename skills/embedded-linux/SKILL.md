---
name: embedded-linux
description: Yocto LTS policy, BSP structure, verified boot, OTA, hardening. Use when shipping Linux on MPU/SoC products.
version: 1.2.0
domains: [generic-embedded, automotive, industrial, iot, robotics]
platforms: [mpu, soc, mpsoc, linux]
---

# Embedded-Linux skill

Production Linux for MPU/SoC/MPSoC targets: Yocto-built images, kernel and
device-tree configuration, bootloader integration, OTA update, hardening, and
real-time behavior — with licensing and long-term maintenance handled
explicitly.

## 1. Purpose and scope

**Purpose.** Ship a maintainable, reproducible, updatable Linux system on
resource-constrained hardware with a documented BSP, update story, and
security posture.

**In scope.** Yocto Project builds, kernel configuration (including
PREEMPT_RT), device trees, U-Boot integration, rootfs design, OTA update
(A/B or delta), secure boot and runtime hardening, software licensing (SBOM,
copyleft compliance), and LTS maintenance planning.

**Non-goals.** Desktop Linux administration, container orchestration at scale,
and application-level development (covered by domain skills). This skill owns
the platform the applications run on.

**How to use.** Pick the Yocto LTS per §3, define the machine/BSP per §4,
configure kernel and device tree per §5, wire boot and OTA per §6, harden per
§7, and plan maintenance per §8.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | Yocto Project Wrynose | 6.0 LTS, released April 2026, supported to 2030; kernel 6.18, GCC 15.2 | Current LTS for new designs | `https://www.yoctoproject.org/blog/2026/04/30/yocto-project-6-0-releases/` |
| 2 | Yocto Project Scarthgap | 5.0 LTS, supported to 2028; prior LTS | Maintenance baseline for existing products | `https://docs.yoctoproject.org/migration-guides/release-5.0.html` |
| 3 | Linux kernel PREEMPT_RT | Mainline since 6.12 (real-time preemption merged) | Deterministic latency path for control workloads | `https://www.kernel.org/` |
| 4 | U-Boot verified boot | Current (secure-boot / FIT signature framework) | Bootloader stage of the trust chain | `https://docs.u-boot.org/en/latest/usage/secure_boot.html` |
| 5 | SPDX SBOM | ISO/IEC 5962:2021, SPDX 2.3/3.0 | License inventory and vulnerability tracking format | `https://spdx.dev/` |

## 3. Distribution choice — Yocto LTS policy

| Release | Status | Support until | Use for |
|---------|--------|---------------|---------|
| Wrynose 6.0 | Current LTS (April 2026) | 2030 | All new designs started after April 2026 |
| Scarthgap 5.0 | Prior LTS | 2028 | Existing products; migrate before EOL |
| Non-LTS (e.g. 4.x, 5.x STS) | Short-lived | ~7 months | Evaluation and upstream contribution only |

**Rules.**

- New products start on the current LTS (Wrynose 6.0). Starting on a
  short-term-support release without a written migration plan is a blocking
  review finding.
- Pin `DISTRO`, machine, and all layer revisions in the build manifest
  (`kas`, repo manifest, or locked submodules). Unpinned floating layers are
  not reproducible and fail the maintenance gate (§8).
- Keep a vendor kernel only when mainline lacks required drivers; record the
  forward-port plan and rebase cadence in the BSP README.

## 4. BSP structure — machine, kernel, device tree

1. **Machine definition.** One `MACHINE` per board revision with distinct
   device trees; never overload one machine with per-revision shell
   conditionals that change the ABI.
2. **Kernel configuration.** Maintain `defconfig` + fragments (`cfg/`), not a
   hand-edited `.config`. Fragments are named by concern
   (`debug.cfg`, `rt.cfg`, `security.cfg`) so production (`linux-prod`)
   disables debug paths by construction.
3. **Device tree.** Hardware description lives in `.dts`/`.dtsi` includable per
   board variant; no board-specific `#ifdef` in drivers. Every peripheral used
   in production has a `status = "okay"` audit: disabled-by-default nodes must
   be justified or removed.
4. **Drivers.** Prefer mainline drivers; out-of-tree modules require a DKMS or
   Yocto recipe with version pinning, license declaration, and a mainline
   upstreaming or removal plan.

## 5. Real-time behavior (when the system has deadlines)

1. **Decide RT need first.** Hard control loops (motor, power, motion) belong
   on an MCU or RTOS coprocessor (see `mcu`, `rtos`); Linux handles
   supervisory, networking, and HMI roles. If Linux itself has deadlines,
   enable PREEMPT_RT (mainline since 6.12) and measure — never assume.
2. **Measure latency.** `cyclictest` under full load (network, storage, GPU)
   defines the achievable deadline; record max observed latency with
   configuration, load profile, and kernel version.
3. **Isolate.** `isolcpus`/`cpusets` for RT tasks, threaded IRQs, priority
   inheritance mutexes, and mlockall to prevent paging. No RT task shares a
   core with uncharacterized best-effort load without measurement evidence.

## 6. Boot chain and OTA update

1. **Verified boot.** ROM → U-Boot (FIT signature verification) → signed
   kernel → dm-verity protected rootfs. Each stage verifies the next before
   execution; verification failures halt or fall back — never continue
   unverified.
2. **OTA design.** A/B partition scheme (or verified delta equivalent) with
   atomic switch, automatic rollback on failed self-test, and versioned
   compatibility metadata. Devices must survive power loss at any point in
   the update without bricking.
3. **Update testing.** Every release exercises: successful update, rollback on
   bad image, power-loss injection mid-write, and downgrade-attack rejection
   (anti-rollback version check).

## 7. Hardening and licensing

**Hardening baseline.**

- Minimal image: no compiler, no package manager, no debug shell on production
  images. Remove `packagegroup-core-tools-debug` equivalents.
- Read-only rootfs with dm-verity; writable state confined to encrypted data
  partitions.
- Mandatory access control (SELinux or AppArmor policy shipped and enforcing),
  seccomp filters on network-facing services, kernel module signing enforced.
- Unique per-device credentials; no default passwords; SSH key-only or disabled.

**Licensing.**

- Generate an SPDX SBOM per release build; track CVEs against it in CI.
- Copyleft audit: identify GPL/LGPL components, publish required sources, and
  keep proprietary userspace out of GPL-linked kernel modules (no `EXPORT_SYMBOL_GPL`
  abuse — legal review, not a technical workaround).

## 8. Maintenance gates (blocking)

1. Build manifest pins every layer; `bitbake` reproduces the image from clean
   state (sstate documented, not required for reproducibility claim).
2. SBOM generated and CVE scan clean or with documented waivers + expiry dates.
3. Verified-boot chain demonstrated end to end on hardware.
4. OTA update + rollback + power-loss tests pass on hardware.
5. RT latency characterized (if deadlines claimed) with recorded max and
   configuration.
6. LTS EOL date recorded in the product plan with a migration trigger no later
   than 12 months before EOL.

## 9. Verification of this skill (Phase 4 gate)

- Yocto releases carry version + support window + URL (§2, §3).
- No floating-layer or unverified-boot design passes review (§3, §6).
- Licensing and CVE evidence in `schemas/compliance-evidence.schema.json`.
