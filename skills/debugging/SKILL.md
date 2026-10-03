# Debugging skill

Systematic defect diagnosis on target hardware: reproduce, isolate, root-cause,
fix, and prevent — with debuggers, trace, logic analysis, and post-mortem
discipline that turns each bug into process improvement.

## 1. Purpose and scope

**Purpose.** Find true root causes (not symptoms) efficiently and convert each
significant defect into a regression test plus a prevention action.

**In scope.** Reproduction strategy, on-target debug (JTAG/SWD, semihosting,
RTT), trace (ETM/ITM, logic analyzer, protocol decoders), fault capture
(`bare-metal` §3 handlers, crash dumps, watchdogs as witnesses), bisection,
and defect-prevention feedback (tests, checkers, checklist updates).

**Non-goals.** Production monitoring (see `validation`, `ai-validation` §6)
and lab administration. Starts at a defect report, ends at a verified fix with
prevention in place.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | IEEE 1044 Anomaly classification | 2009 (reaffirmed) | Defect taxonomy: severity, cause, source, type — for consistent records | `https://standards.ieee.org/standard/1044-2009.html` |
| 2 | IEEE 829 Test documentation (anomaly reporting concepts) | 2008 (withdrawn; concepts retained as practice) | Anomaly report fields; cite as practice, note withdrawn status | `https://standards.ieee.org/` |
| 3 | Arm CoreSight architecture | Current (SoC-600 / CoreSight technology) | ETM/ITM/trace infrastructure capabilities | `https://www.arm.com/architecture/system-architectures/coresight-architecture` |

## 3. Method — reproduce, isolate, root-cause

1. **Reproduce first.** No code changes until the failure reproduces on demand
   (script, test, or documented manual sequence); intermittent bugs get
   long-run traps (watchdog logs, trace buffers, stress loops) before
   theorizing.
2. **Isolate by halves.** Bisect in time (when did it start — `git bisect`,
   binary search over builds), in space (which task/driver/input), and in
   configuration (which option flips it). One variable at a time.
3. **Read the silicon's testimony.** Fault registers, stacked PC/LR, ITM
  printf, ETM trace, analyzer captures — collect hardware evidence before
   forming hypotheses. The `bare-metal` speaking-fault-handler output is the
   minimum starting exhibit.
4. **Five whys to process.** Root cause is the process gap that let the defect
   in (missing test, unchecked erratum, wrong assumption documented nowhere),
   not just the bad line. Fix the line and the gap.

## 4. Fix and prevention rules

1. **Minimal fix, reviewed.** Smallest change that removes the root cause;
   speculative hardening in the same change is a separate commit.
2. **Regression test mandatory.** Every fixed defect gains a test that fails
   without the fix (unit, HIL, or trace-replay); fixes without tests are
   rejected except where physically untestable (waiver + rationale).
3. **Prevention action.** Update the checklist, rule, or checker that should
   have caught it (`code-review` checklists, `static-analysis` rulesets,
   `unit-test` patterns) — the defect class must not recur silently.

## 5. Release gates (blocking)

1. All known blocking/major defects fixed or formally waived with rationale
   and expiry.
2. Every fix traced to a regression test; defect metrics (density, escape
   rate, mean time to root-cause) reviewed per increment.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL, withdrawn status
  honestly noted (§2.2).
