---
name: performance
description: >
  Top-down budgets, WCET measurement, profile-before-patch, CI tripwires. Use
  when meeting latency, throughput, or determinism targets.
version: 1.2.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.performance
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: [axiom-memory-and-performance-analysis]
  checklists: [checklists/performance-checklist.md]

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
# Performance skill

Timing, throughput, memory, and power performance for embedded targets:
budgeting from architecture, measurement on hardware, and optimization that
never trades away correctness, safety margins, or determinism silently.

## 1. Purpose and scope

**Purpose.** Meet every timing deadline, throughput target, and resource budget
with measured headroom -- and prove it with numbers from hardware.

**In scope.** Performance budgeting (CPU, bus, memory bandwidth, power),
WCET analysis and measurement, profiling on target, optimization techniques
(algorithmic, cache/DMA layout, compiler), power/latency trade decisions, and
regression tracking in CI.

**Non-goals.** Functional correctness (see `implementation`, test skills) and
hard-real-time scheduling proofs (see `rtos` S5). Ends at met budgets with
recorded margins and a regression tripwire.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-6 Software level | 2018 | Clause 9: timing and resource-usage verification for safety software | `https://www.iso.org/standard/68388.html` |
| 2 | MLPerf Tiny | v1.x | Latency/energy measurement methodology reference | `https://mlcommons.org/benchmarks/mlperf-tiny/` |
| 3 | SPEC telemetry practice | Current embedded profiling practice | Measure-on-target, worst-case-corner methodology | Vendor profiler documentation |

## 3. Budgeting rules

1. **Budgets allocated top-down.** System deadlines decompose into per-task,
   per-ISR, and per-transfer budgets at architecture time (`architecture` S3);
   unbudgeted paths are found by profiling, not by field failures.
2. **WCET, not average.** Real-time claims use measured worst case at the
   worst-case corner (low voltage, high temperature, max clock drift) under
   full system load -- averages are for dashboards, WCET is for guarantees.
3. **Bandwidth is a budget too.** DMA, bus, and memory-bandwidth consumers are
   summed against the interconnect capacity (`soc`/`mpsoc` NoC budgets);
   cache effects measured, not modeled optimistically.

## 4. Measurement discipline

1. **On target, instrumented honestly.** GPIO toggles, cycle counters (DWT/
   PMU), and trace (ETM/ITM where available); measurement overhead quantified
   and subtracted or bounded.
2. **Profiles before patches.** No optimization without a profile showing the
   hotspot; every optimization re-profiled after, with before/after numbers in
   the commit message.
3. **Regression tripwires.** Key metrics (loop WCET, ISR duration, inference
   latency, boot time, idle current) tracked in CI with thresholds; regressions
   block like test failures.

## 5. Optimization guardrails

Algorithmic wins before micro-tuning; cache/DMA layout before assembly;
compiler flags project-wide and reviewed (`-O2` vs `-Os` vs `-O3` justified
per binary). Optimizations that hurt determinism (speculative Davey paths,
unbounded prefetch effects) or safety margins require `safety` review. Power
optimizations (sleep modes, DVFS, clock gating) verified against latency
budgets -- a missed deadline from a sleep transition is a defect, not savings.

## 6. Release gates (blocking)

1. All timing/resource budgets met at worst-case corner with recorded margin.
2. WCET evidence for every deadline path; tripwires green in CI.
3. Power budget met at product duty cycle with energy-per-task numbers.
4. No optimization without profile evidence; no determinism trade without review.

## 7. Verification of this skill (Phase 4 gate)

- Timing claims measured on hardware at worst-case corner (S4), never host
  extrapolations.






## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.



## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

| Rule | Standard clause | Impact |
|---|---|---|
| R1 | (none declared) | LOW |


## Impact tiers

| Tier | Meaning |
|---|---|
| CRITICAL | Safety/security-critical; requires human approval and impact assessment |
| HIGH | Significant impact; requires review |
| MEDIUM | Moderate impact; standard review |
| LOW | Minor impact; routine review |

### Rule impact assignments

All rules in this skill default to MEDIUM unless marked CRITICAL or HIGH
in the rule ID -> clause map above.

## Deviation management

Any deviation must be recorded with: Rule ID, reason, file/location,
approver, and date. CRITICAL-rule deviations require safety-lead approval
and an impact assessment. Deviations are first-class artifacts, not comments.


## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.

