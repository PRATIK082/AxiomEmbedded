---
name: soc
description: >
  Heterogeneous SoC allocation across A/R cores, NPUs, safety islands,
  power/thermal. Use when architecting multi-core SoC products.
version: 1.2.0
domains: [generic-embedded, automotive, industrial, robotics]
platforms: [soc, mpsoc]

axiom:
  dotted_name: axiom.legacy.soc
  domain: generic-embedded
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: [axiom-zonal-architecture]
  checklists: [checklists/soc-checklist.md]

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
# SoC skill

Single-die system integration: combining processors, accelerators, memory,
and I/O on one chip (or chip family) with coherent architecture, power and
thermal design, and a software-visible contract the BSP can actually implement.

## 1. Purpose and scope

**Purpose.** Define and integrate SoC-based products where the differentiation
is in the combination -- application cores plus real-time cores, NPU/DSP,
safety islands, and high-speed I/O -- with all cross-domain interactions
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
   software function names its core in the deployment view (`architecture` S3).
2. **Inter-core communication specified.** Shared-memory protocols, mailbox/IPI
   semantics, RPMsg or equivalent versioning, and endianness/cache-coherency
   handling are interface artifacts (see `architecture` S3.4) -- ad-hoc shared
   structs without a protocol owner are defects.
3. **Freedom from interference across cores.** Safety-island isolation
   demonstrated (bus guardians, memory partitioning, independent clocks where
   claimed); non-safety cores cannot stall safety paths -- verified by
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
   and power domains -- custom SMC interfaces minimized and documented where
   unavoidable. The BSP consumes these; it does not reimplement them.

## 5. Handoff gates (blocking)

1. Core allocation complete with interference argument (safety island where
   integrity levels demand it).
2. Inter-core protocols specified, versioned, and reviewed.
3. Power/thermal analysis closes at worst-case corner with tested throttling.
4. Firmware interface list (PSCI/SCMI/custom) agreed with the BSP team.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + URL (S2).
- No tape-out or board spin without the S5 handoff artifacts.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| security-secure-enclave | Secure enclave | HIGH |
| safety-interference | Freedom from interference | MEDIUM |
| hardware-thermal-budget | Thermal budget | MEDIUM |
| power-management-domains | Power domain management | MEDIUM |
| firmware-interface-contract | PSCI/SCMI interface | LOW |

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
| security-secure-enclave | HIGH |
| safety-interference | MEDIUM |
| hardware-thermal-budget | MEDIUM |
| power-management-domains | MEDIUM |
| firmware-interface-contract | LOW |

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

This skill produces reviewable artifacts. Its outputs must be
independently checked by a human reviewer or the domain review skill
before acceptance; solo use requires an explicit waiver recorded in
the deviation log.

## Three-zone autonomy

Autonomy is zoned by risk; the V&V boundary is the automation boundary.

- Core / evidence zone (AI no access, human accountable): certified or
  qualified artifacts, evidence records, safety/security-critical code, and
  release baselines. AI must not read or write here without an explicit
  human-approved change request.
- Gray zone (AI assistant + HITL): AI plans and drafts; a human decides and
  approves each step. Architecture, requirements, tests with safety impact,
  and verification-affecting configuration live here.
- Non-critical zone (AI unrestricted): documentation, examples, scaffolding,
  low-risk refactors, and tooling glue.

This skill's outputs are treated as gray-zone by default; AI may draft but
a human approves. AI must never act autonomously in the core/evidence zone.

