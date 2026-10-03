---
name: automotive-cybersecurity
description: ISO/SAE 21434 TARA, CAL-based rigor, CSMS/SUMS evidence for R155/R156. Use for item definition, threat analysis, security goals, secure design, verification, incident response, or cybersecurity cases.
version: 1.2.0
domains: [automotive]
platforms: [all]
---

# Automotive Cybersecurity skill

Road-vehicle cybersecurity per ISO/SAE 21434 with regulatory evidence for UNECE R155
(CSMS) and R156 (SUMS): item definition → TARA → security concept → secure design →
verification → incident response → cybersecurity case. Complements `safety` and
`security` — coordinate, never conflate.

## 1. Objectives, Prerequisites, Outcomes, Time, Resources

### Objectives

1. Define items, boundaries, operational environment per 21434 concept phase.
2. Execute TARA: assets → threats → attack paths → impact x feasibility → risk → treatment.
3. Assign CAL, derive security goals/requirements, design controls (HSM/TEE/SHE, SecOC,
   MACsec/TLS, secure boot/OTA, key lifecycle, IdsM).
4. Verify per CAL (fuzz, vuln-scan, pen-test) and assemble cybersecurity case + CSMS/SUMS pack.

### Prerequisites

- Item architecture draft (E/E topology, interfaces, ECUs, data flows) and lifecycle scope.
- `safety` HARA if safety-related; `autosar` context if applicable.
- Evidence schemas (`schemas/traceability-matrix.schema.json`, `schemas/compliance-evidence.schema.json`).

### Outcomes

- Item definition, TARA report, cybersecurity plan, security goals + requirements,
  architecture with control allocation, V&V reports, vulnerability/incident records,
  cybersecurity case, CSMS/SUMS audit pack. Gap-free traceability throughout.

### Time

- Initial TARA (single item, 5–10 assets): 2–5 days. Full concept-to-case: 4–10 weeks.
  Re-assessment on architecture change, new interface, CVE/incident, OTA major.

### Resources (metadata only)

| # | Source | Version | URL |
|---|--------|---------|-----|
| 1 | ISO/SAE 21434 | 1st ed. 2021 | `https://www.iso.org/standard/70918.html` |
| 2 | UNECE R155 + CSMS | In force 2021 | `https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security` |
| 3 | UNECE R156 + SUMS | In force 2021 | `https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update` |
| 4 | NIST SP 800-193 | Rev. 1 (2024) | `https://csrc.nist.gov/pubs/sp/800/193/r1/final` |
| 5 | EVITA / HEAVENS | 2008–2011 / v2.0 2016 | `https://www.evita-project.org/` |
| 6 | ISO 26262 (coordination) | 2nd ed. 2018 | `https://www.iso.org/standard/68383.html` |

## 2. Purpose and scope

Repeatable 21434 lifecycle from item definition to assessable cybersecurity case.
In scope: item definition, TARA, CAL, goals/requirements, secure design, verification,
vulnerability management, incident response, decommissioning, case assembly.
Non-goals: no type approval, no CSMS/SUMS certification, no normative text reproduction.
Boundary: `security` owns generic device hygiene; this skill owns vehicle-specific rigor
(item semantics, CAL, SecOC/IdsM/SHE, R155/R156 work products, cybersecurity case).

## 3. Item definition (entry gate)

1. Item boundary: function, E/E decomposition, ECUs, out-of-scope dependencies.
   Interface inventory (CAN/Ethernet, LIN, OBD-II, UDS, BT/Wi-Fi/UWB, cellular/V2X, debug).
2. Operational environment: use cases, modes, actors (occupants, backend, aftermarket),
   attacker proximity (remote / short-range / physical).
3. Assets + security properties per asset (C/I/A + authenticity where relevant), trust boundaries.
4. Assumptions + dependencies (project-authored only).
5. Exit: every external interface has owner, trust level, and at least one asset flowing over it.

## 4. TARA workflow (step-by-step)

1. Asset identification (firmware, keys/certs, calibration, PII, safety signals, OTA packages).
2. Threat scenarios: STRIDE per interface + EVITA/HEAVENS automotive families.
3. Attack paths as attack trees (AND/OR, shared sub-trees, safety branches flagged).
4. Impact rating (Safety/Financial/Operational/Privacy: Severe/Major/Moderate/Negligible);
   Safety corroborated with `safety` HARA.
5. Attack feasibility (elapsed time, expertise, knowledge, access, equipment → High/Medium/Low/Very Low).
6. Risk determination (Impact x Feasibility → Risk 1–5) with versioned matrix.
7. Treatment: avoid / reduce (goal + requirements) / share / retain (rationale + sign-off).
   Retaining Risk ≥ 3 without treatment is blocking.
8. Maintenance: re-run on new interface/asset/architecture change/CVE/OTA major/audit finding.

## 5. CAL levels

| CAL | Risk signal | Rigor signal |
|-----|-------------|--------------|
| CAL 1 | Risk 1–2 | Standard process; peer review; baseline V&V |
| CAL 2 | Risk 2–3 | Structured reviews; coverage-guided fuzz; vuln-scan in CI |
| CAL 3 | Risk 3–4, safety/fleet-scalable | Independent verification; systematic pen-test; IdsM validation |
| CAL 4 | Risk 4–5, severe at scale | Independent assessment; red-team; full assurance case |

Rules: CAL follows highest residual risk; decomposition only with independence argument;
never equate CAL = ASIL = SIL.

## 6. Security goals and requirements chain

1. Goals: one per unacceptable scenario, technology-neutral, verifiable, with CAL + secure-state.
2. Product requirements: system/HW/SW with ID, CAL, component, pre/post-conditions,
   verification method, evidence pointer (e.g. `SEC-GOAL-03 → SEC-SYS-12 (SecOC) →
   SEC-HW-04 (HSM) → SEC-SW-21 (freshness ≤ 2 frames)`).
3. Process requirements (CSMS): roles, gates, supplier agreements, tool management, SLA handling.
4. SUMS requirements (R156): SW identification, integrity/authenticity, dependency checks,
   rollback-safe behavior, notification, campaign audit logging.
5. Rule: every Risk ≥ 2 scenario has ≥1 goal and ≥1 verifiable requirement.

## 7. Security controls catalog

| Family | Baseline (CAL1–2) | Advanced (CAL3–4) |
|--------|-------------------|-------------------|
| HW trust anchor | SHE / secure-element; ROP + debug lock | HSM or TEE with measured boot; side-channel countermeasures |
| Secure boot | Verify-before-jump; anti-rollback | Redundant/recovery image; NIST 800-193 protection+detection+recovery on HW |
| OTA | Signed packages; version manifest | End-to-end SUMS flow + install attestation + rollback + campaign audit |
| In-vehicle auth | CAN filtering; UDS 0x27 sessions | SecOC with freshness; MACsec backbone; TLS 1.2+ off-board |
| Key lifecycle | Per-device unique keys; no hard-coded keys | HSM provisioning; rotation/revocation drills; offline root; zeroization |
| Intrusion detection | Security event logging | AUTOSAR IdsM + CAN anomaly rules; SOC feed with SLAs |
| Hardening / FFI | MPU/MMU partitioning | FFI argument vs `safety`; time partitioning; WCET-bounded monitors |

No custom crypto. Keys in secure storage, never in images or repos.

## 8. Verification per CAL

| Activity | CAL 1–2 | CAL 3–4 |
|----------|---------|---------|
| Requirements review | Required | + independent assessor |
| Fuzz (CI) | All external parsers | + stateful protocol + bus-level oracles |
| Vuln scanning | SBOM + CVE per release | Continuous + exploitability + SLA triage |
| Pen-test | Sampled interfaces | Systematic per attack path; red-team at CAL 4 |
| Boot/OTA demo | On HW, signed + rollback rejected | + glitch spot-checks; recovery boot proven |
| Key audit | Algorithm + storage review | + ceremony witness + rotation drill |
| Confirmation | Cybersecurity audit | + independent assessment |

## 9. Traceability and compliance mapping

Chain: `Asset → Threat → Attack path → Risk → Treatment → Goal [CAL] → Requirement →
Architecture/control → Code/config → Test → Evidence → Case claim.` Orphan nodes block gates.
ASPICE neighbors: item/plan → SYS.1–2/MAN.3; TARA/goals → SYS.2–3; requirements/arch →
SYS.3–4/SW.1–2; implementation → SW.3/SWE.4–6; integration/pen-test → SYS.4–5;
CSMS/SUMS audit → SUP.1/8/9/MAN.3. Safety coordination: joint review of safety-impacting
threats; secure-state vs safe-state conflicts resolved explicitly (SecOC drop vs FTTI).

## 10. Work products, evidence, sign-off gates (blocking, human approval)

Work products: plan, item definition, TARA report, risk/treatment log, goals/requirements,
architecture + CAL rationale, V&V reports, vulnerability + incident records, case, audit pack.
Gates: (1) item complete; (2) TARA covers all interfaces, Risk ≥ 3 treated; (3) CAL assigned;
(4) goals→requirements→controls traced; (5) controls demonstrated on HW; (6) fuzz/scan/
pen-test green or waiver-documented; (7) incident SLAs published, audit pack linked;
(8) independent assessment recorded with findings dispositioned.

## 11. Verification of this skill

Normative sources cited with number + version + clause + URL; TARA executable in order;
CAL table without CAL=ASIL equivalence; controls catalog complete; V&V differentiates
CAL 1–2 vs 3–4; traceability + ASPICE/safety mapping present; eight gates enforce approval.

Load task-specific domain/platform/rule overlays before execution.
