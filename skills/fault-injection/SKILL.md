# Fault-Injection skill

Deliberate fault campaigns that prove safety mechanisms work: hardware faults
(voltage, clock, SEU), software faults (bit flips, stuck values, message
loss), and the diagnostic-coverage evidence safety cases depend on.

## 1. Purpose and scope

**Purpose.** Demonstrate that every claimed safety mechanism actually detects,
contains, or mitigates its faults within the fault-tolerant time interval —
with measured diagnostic coverage, not assumed.

**In scope.** Fault-list derivation from FMEA/FTA, SWIFI/HWIFI/physical fault
methods, campaign design and sampling rationale, result classification, and
diagnostic-coverage computation feeding FMEDA and the safety case (`safety` §6).

**Non-goals.** Reliability prediction (FIT/MTBF math lives in FMEDA) and
security fault attacks (see `security` — coordinate methods, separate claims).
Ends at coverage numbers the assessor can reproduce.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-5 Hardware level | 2018 | Clauses 8–9: SPFM/LFM targets, fault-injection role in verification | `https://www.iso.org/standard/68387.html` |
| 2 | ISO 26262-6 Software level | 2018 | Clause 9: software verification incl. fault-injection testing | `https://www.iso.org/standard/68388.html` |
| 3 | IEC 61508-7 | 2010 | Annex B: fault-injection and diagnostic techniques overview | `https://webstore.iec.ch/en/publication/5515` |

## 3. Campaign design

1. **Faults from analysis, not imagination.** The fault list derives from the
   FMEA/FTA: every safety mechanism names the faults it claims to handle, and
   every listed fault gets injected. Unlisted-but-plausible faults found during
   review extend the list — the list is a living artifact.
2. **Three injection levels.** Software-implemented (bit flips, API error
   returns, message drops/delays) for breadth; hardware-implemented
   (voltage/clock glitch, pin faults) for physical realism on sampled cases;
   simulation-based (stuck-at in netlists, saboteurs in models) for early
   coverage. Level chosen per claim, recorded per result.
3. **Sampling with rationale.** Exhaustive injection is infeasible; the sampling
   strategy (random weighted by failure-rate, or directed at uncovered
   mechanisms) is documented with confidence arguments the assessor can follow.

## 4. Execution and classification

Every injection run classifies as: **detected-safe** (mechanism caught it,
safe state reached in FTTI), **detected-unsafe**, **undetected-safe** (benign),
or **undetected-unsafe** (the dangerous class — each one opens a defect with
severity tied to the violated safety goal). Undetected-unsafe results block
release until mitigated and re-campaigned.

## 5. Coverage accounting

Diagnostic coverage per mechanism = detected-safe / (total − proven-benign),
rolled into FMEDA SPFM/LFM against the ASIL targets (`safety` §5): ASIL D
SPFM ≥ 99% / LFM ≥ 90%, ASIL C 97%/80%, ASIL B 90%/60%. Coverage claims cite
campaign ID, sample size, and classification ledger — reproducible from raw
logs.

## 6. Release gates (blocking)

1. Fault list traced to FMEA/FTA; every safety mechanism has fault cases.
2. Injection levels justified per claim; sampling rationale recorded.
3. Zero open undetected-unsafe results.
4. Coverage numbers computed and meeting ASIL targets; ledger archived.
5. Results packaged per `safety` §7 evidence schema.

## 7. Verification of this skill (Phase 4 gate)

- No coverage number without a reproducible campaign behind it (§5).
- Safety-sensitive content → human review flag on verification.
