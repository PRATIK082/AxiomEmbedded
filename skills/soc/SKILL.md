# SoC skill

Single-die system integration: combining processors, accelerators, memory,
and I/O on one chip (or chip family) with coherent architecture, power and
thermal design, and a software-visible contract the BSP can actually implement.

## 1. Purpose and scope

**Purpose.** Define and integrate SoC-based products where the differentiation
is in the combination — application cores plus real-time cores, NPU/DSP,
safety islands, and high-speed I/O — with all cross-domain interactions
specified.

**In scope.** SoC selection and comparison, heterogeneous core allocation
(A-cores vs R-cores vs DSP/NPU), interconnect and coherency (ACE/CHI concepts
at system level), power domains and DVFS policy, thermal design, safety-island
integration, and the hardware-to-software handoff (memory map, interrupts,
clocks, firmware interfaces like SCMI/PSCI).

**Non-goals.** Board-level MPU integration details (see `mpu`), full-custom
silicon design. Assumes one integrated die; multi-die coherent fabrics belong
to `mpsoc`.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | Arm PSCI / SCMI | PSCI 1.1+, SCMI v3.x | CPU power-state and system-control firmware interfaces | `https://developer.arm.com/documentation/den0022/latest/` |
| 2 | Arm AMBA ACE/CHI | Current specifications | Coherency protocol concepts for core-to-core and accelerator sharing | `https://developer.arm.com/documentation/` |
| 3 | MIPI CSI/DSI / PCIe / Ethernet TSN | Current specifications | High-speed peripheral integration contracts | `https://www.mipi.org/specifications` |
| 4 | ISO 26262-11 Semiconductors | 2018 (Part 11 guideline) | Semiconductor safety integration expectations | `https://www.iso.org/standard/69349.html` |

## 3. Heterogeneous allocation rules

1. **Right core for the job.** Hard real-time and safety monitors on R-class
   / lockstep cores or the safety island; supervisory, networking, and HMI on
   A-cores under Linux; ML on NPU/DSP via the `edge-ai` delegate path. Every
   software function names its core in the deployment view (`architecture` §3).
2. **Inter-core communication specified.** Shared-memory protocols, mailbox/IPI
   semantics, RPMsg or equivalent versioning, and endianness/cache-coherency
   handling are interface artifacts (see `architecture` §3.4) — ad-hoc shared
   structs without a protocol owner are defects.
3. **Freedom from interference across cores.** Safety-island isolation
   demonstrated (bus guardians, memory partitioning, independent clocks where
   claimed); non-safety cores cannot stall safety paths — verified by
   interference testing, not architecture slides.

## 4. Power, thermal, and firmware interfaces

1. **Power domains mapped to use cases.** Each operating mode (active, idle,
   suspend, safety-only) names its powered domains and transition latencies;
   DVFS policy owned by software with thermal-trip behavior specified and
   tested.
2. **Thermal budgeted.** Junction-temperature analysis at worst-case workload
   and ambient; throttling policy defined before it is discovered in the field
   (throttle points are requirements with verification, see `requirements`).
3. **Firmware interfaces standard.** PSCI for CPU power states, SCMI for clocks
   and power domains — custom SMC interfaces minimized and documented where
   unavoidable. The BSP consumes these; it does not reimplement them.

## 5. Handoff gates (blocking)

1. Core allocation complete with interference argument (safety island where
   integrity levels demand it).
2. Inter-core protocols specified, versioned, and reviewed.
3. Power/thermal analysis closes at worst-case corner with tested throttling.
4. Firmware interface list (PSCI/SCMI/custom) agreed with the BSP team.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + URL (§2).
- No tape-out or board spin without the §5 handoff artifacts.
