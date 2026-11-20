---
name: mpsoc
description: >
  MPSoC NoC QoS, coherency domains, PL-as-hardware timing closure, cross-die
  safety. Use for FPGA-SoC or multi-die platforms. Use when mpsoc tasks arise in
  generic-embedded projects.
version: 1.2.0
domains: [generic-embedded, automotive, aerospace, defense, industrial]
platforms: [mpsoc, soc]

axiom:
  dotted_name: axiom.legacy.mpsoc
  domain: generic-embedded
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: [axiom-zonal-architecture]
  checklists: [checklists/mpsoc-checklist.md]

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
# MPSoC skill

Multi-die and large-fabric integration: coherent multi-cluster compute,
chiplet/interconnect architecture, high-bandwidth memory, and the system-level
verification that proves the fabric meets latency, bandwidth, and safety
claims under concurrent load.

## 1. Purpose and scope

**Purpose.** Architect products on multi-die SoCs (application + real-time +
programmable logic, or multi-cluster compute fabrics) where the dominant risks
are interconnect performance, coherency correctness, and cross-die safety
partitioning.

**In scope.** MPSoC selection, cluster and programmable-logic allocation,
cache-coherency domains, NoC bandwidth/latency budgeting, HBM/DDR multi-port
memory architecture, cross-die safety partitioning, and system-level
performance verification.

**Non-goals.** Single-die integration (see `soc`), board design (see `mpu`).
This skill owns the fabric; `soc` owns the die-level contract.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | Arm AMBA CHI | Current (issue F+) | Coherent Hub Interface for scalable multi-cluster fabrics | `https://developer.arm.com/documentation/` |
| 2 | UCIe chiplet interconnect | 1.x/2.0 (in evolving release) | Die-to-die interface expectations; record the revision used | `https://www.uciexpress.org/specifications` |
| 3 | CCIX / CXL coherency concepts | Current specifications | Accelerator/memory coherency models where applicable | `https://www.computeexpresslink.org/` |
| 4 | ISO 26262-9 ASIL decomposition | 2018, S5 | Cross-die independence arguments for decomposed requirements | `https://www.iso.org/standard/68391.html` |

## 3. Fabric architecture rules

1. **Budget the NoC like a schedule.** Every initiator's bandwidth and latency
   requirement is quantified; the NoC QoS configuration (priorities, rate
   limiters, virtual channels) is derived from those budgets and reviewed --
   default QoS on a shared fabric is a blocking finding.
2. **Coherency domains explicit.** Which masters share coherency, where
   software-managed coherence (flushes/invalidates) is required, and the exact
   sequences -- documented per data path (camera->NPU->CPU, PL->DDR->CPU). Wrong
   assumptions here corrupt data silently.
3. **Programmable logic treated as hardware.** PL bitstreams are versioned
   design artifacts with timing closure evidence and interface contracts
   (AXI boundaries specified); bitstream/config compatibility is part of the
   OTA story (`embedded-linux` S6).
4. **Memory ports allocated.** HBM/DDR ports assigned to traffic classes with
   headroom; concurrent worst-case traffic analyzed, not hoped.

## 4. Cross-die safety and security

1. **Partitioning across dies.** Safety functions confined to dies/domains with
   demonstrated independence (separate power, clock, and reset where the ASIL
   demands it); cross-die safety signals use protected protocols (CRC,
   redundancy, timeout supervision) per `safety` S5.
2. **Secure boot across the fabric.** Every die's firmware authenticated in the
   boot chain; PL bitstreams signed and verified like software images.

## 5. Verification gates (blocking)

1. NoC budgets quantified per initiator with QoS configuration reviewed.
2. Coherency sequences documented per data path and tested under concurrent load.
3. PL timing closure and AXI contracts evidenced per bitstream release.
4. Cross-die safety partitioning demonstrated by interference and fault-injection
   testing (`safety` S6).
5. Worst-case concurrent performance measured on hardware or cycle-accurate
   models -- never from spreadsheet addition.

## 6. Verification of this skill (Phase 4 gate)

- Interconnect revisions (CHI issue, UCIe rev) recorded where claimed (S2).
- No performance claim without measured concurrent-load evidence (S5.5).

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| safety-interference-testing | Freedom from interference | HIGH |
| security-secure-enclave | Secure enclave / TEE | MEDIUM |
| realtime-noc-qos | NoC QoS configuration | MEDIUM |
| hardware-coherency-protocol | Cache coherency (CHI/ACE) | MEDIUM |
| thermal-power-envelope | Thermal/power envelope | LOW |

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
| safety-interference-testing | HIGH |
| security-secure-enclave | MEDIUM |
| realtime-noc-qos | MEDIUM |
| hardware-coherency-protocol | MEDIUM |
| thermal-power-envelope | LOW |

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

