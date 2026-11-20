---
name: fault-injection
description: >
  FMEA-derived fault lists, SWIFI/HWIFI levels, and SPFM/LFM accounting. Use
  when proving safe-state behavior under faults.
version: 1.3.0
domains: [generic-embedded, automotive, aerospace, defense, industrial]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.fault-injection
  domain: generic-embedded
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy, vv, fault-injection]

  related_skills: [security, axiom-validation-orchestrator]
  checklists: [checklists/fault-injection-checklist.md]

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

# Fault-Injection skill

Deliberate fault campaigns that prove safety mechanisms work: hardware faults
(voltage, clock, SEU), software faults (bit flips, stuck values, message
loss), and the diagnostic-coverage evidence safety cases depend on.

## 1. Purpose and scope

**Purpose.** Demonstrate that every claimed safety mechanism actually detects,
contains, or mitigates its faults within the fault-tolerant time interval --
with measured diagnostic coverage, not assumed.

**In scope.** Fault-list derivation from FMEA/FTA, SWIFI/HWIFI/physical fault
methods, campaign design and sampling rationale, result classification, and
diagnostic-coverage computation feeding FMEDA and the safety case (`safety` S6).

**Non-goals.** Reliability prediction (FIT/MTBF math lives in FMEDA) and
security fault attacks (see `security` -- coordinate methods, separate claims).
Ends at coverage numbers the assessor can reproduce.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-5 Hardware level | 2018 | Clauses 8-9: SPFM/LFM targets, fault-injection role in verification | `https://www.iso.org/standard/68387.html` |
| 2 | ISO 26262-6 Software level | 2018 | Clause 9: software verification incl. fault-injection testing | `https://www.iso.org/standard/68388.html` |
| 3 | IEC 61508-7 | 2010 | Annex B: fault-injection and diagnostic techniques overview | `https://webstore.iec.ch/en/publication/5515` |

## 3. Campaign design

1. **Faults from analysis, not imagination.** `[CRITICAL]` The fault list
   derives from the FMEA/FTA: every safety mechanism names the faults it
   claims to handle, and every listed fault gets injected. Unlisted-but-
   plausible faults found during review extend the list -- the list is a
   living artifact.
2. **Three injection levels.** `[HIGH]` Software-implemented (bit flips, API
   error returns, message drops/delays) for breadth; hardware-implemented
   (voltage/clock glitch, pin faults) for physical realism on sampled cases;
   simulation-based (stuck-at in netlists, saboteurs in models) for early
   coverage. Level chosen per claim, recorded per result.
3. **Sampling with rationale.** `[HIGH]` Exhaustive injection is infeasible;
   the sampling strategy (random weighted by failure-rate, or directed at
   uncovered mechanisms) is documented with confidence arguments the
   assessor can follow.

## 4. Execution and classification

Every injection run classifies as: **detected-safe** (mechanism caught it,
safe state reached in FTTI), **detected-unsafe**, **undetected-safe** (benign),
or **undetected-unsafe** (the dangerous class -- each one opens a defect with
severity tied to the violated safety goal). Undetected-unsafe results block
release until mitigated and re-campaigned.

## 5. Coverage accounting

Diagnostic coverage per mechanism = detected-safe / (total - proven-benign),
rolled into FMEDA SPFM/LFM against the ASIL targets (`safety` S5): ASIL D
SPFM >= 99% / LFM >= 90%, ASIL C 97%/80%, ASIL B 90%/60%. Coverage claims
cite campaign ID, sample size, and classification ledger -- reproducible from
raw logs.

## 6. Advanced V&V patterns (P1)

### 6.1 Secure boot validation `[CRITICAL]`
Verify the chain: signature verification succeeds for the attested image,
version anti-rollback rejects a downgraded image, recovery image present and
addressable, debug ports in production lock state. Include eFuse timing
checks, QEMU encrypted-flash simulation, and voltage-glitch fault injection
against the secure-boot path.

### 6.2 PSA/SESIP validation `[CRITICAL]`
NIST SP 800-193 resiliency checks for platform firmware update and recovery:
detect, recover, protect. Map each check to evidence; deviations require
approver and expiry.

### 6.3 Co-simulation fault injection `[MEDIUM]`
Use Verilator/SystemC/FPGA co-simulation to inject faults early (stuck-at,
glitch) before hardware availability; promote sampled cases to hardware.

### 6.4 Voltage-glitch campaigns `[HIGH]`
Physical voltage-glitch fault injection against security/safety mechanisms
with FTTI measurement; coordinate with security team, separate claims.

## 7. Release gates (blocking)

1. Fault list traced to FMEA/FTA; every safety mechanism has fault cases.
2. Injection levels justified per claim; sampling rationale recorded.
3. Zero open undetected-unsafe results.
4. Coverage numbers computed and meeting ASIL targets; ledger archived.
5. Results packaged per `safety` S7 evidence schema.

## 8. Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| FI-R1 | ISO 26262-5 Cl. 8-9 | SPFM/LFM targets and fault-injection role |
| FI-R2 | ISO 26262-6 Cl. 9 | Software verification incl. fault injection |
| FI-R3 | IEC 61508-7 Annex B | Fault-injection and diagnostic techniques |

## 9. Verification of this skill (Phase 4 gate)

- No coverage number without a reproducible campaign behind it (S5).
- Safety-sensitive content -> human review flag on verification.

## Workflow

Follow the skill's numbered rules and gates; record per-step evidence in the
run manifest.

## Acceptance

All checklist gates pass; findings carry severity plus evidence plus action.


## Deviation management

Any deviation from a rule or standard must be recorded with: Rule ID, reason,
file/location, approver, and date. Deviations are tracked as first-class
artifacts, not comments. (Straion pattern.)


## Builder + reviewer

This skill follows the builder + reviewer pattern: the builder produces the
artifact, the reviewer independently verifies it before acceptance. No
artifact is accepted without reviewer sign-off.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.


## References

- `references/standard-map.md`
- `references/vv-patterns.md`
