---
name: debugging
description: >
  Reproduce-isolate-root-cause method with silicon testimony and mandatory
  regression tests. Use when hunting field or lab failures.
version: 1.2.0
domains: [all]
platforms: [all]

axiom:
  dotted_name: axiom.legacy.debugging
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: [axiom-trace-analysis]
  checklists: [checklists/debugging-checklist.md]

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
# Debugging skill

Systematic defect diagnosis on target hardware: reproduce, isolate, root-cause,
fix, and prevent -- with debuggers, trace, logic analysis, and post-mortem
discipline that turns each bug into process improvement.

## 1. Purpose and scope

**Purpose.** Find true root causes (not symptoms) efficiently and convert each
significant defect into a regression test plus a prevention action.

**In scope.** Reproduction strategy, on-target debug (JTAG/SWD, semihosting,
RTT), trace (ETM/ITM, logic analyzer, protocol decoders), fault capture
(`bare-metal` S3 handlers, crash dumps, watchdogs as witnesses), bisection,
and defect-prevention feedback (tests, checkers, checklist updates).

**Non-goals.** Production monitoring (see `validation`, `ai-validation` S6)
and lab administration. Starts at a defect report, ends at a verified fix with
prevention in place.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | IEEE 1044 Anomaly classification | 2009 (reaffirmed) | Defect taxonomy: severity, cause, source, type -- for consistent records | `https://standards.ieee.org/standard/1044-2009.html` |
| 2 | IEEE 829 Test documentation (anomaly reporting concepts) | 2008 (withdrawn; concepts retained as practice) | Anomaly report fields; cite as practice, note withdrawn status | `https://standards.ieee.org/` |
| 3 | Arm CoreSight architecture | Current (SoC-600 / CoreSight technology) | ETM/ITM/trace infrastructure capabilities | `https://www.arm.com/architecture/system-architectures/coresight-architecture` |

## 3. Method -- reproduce, isolate, root-cause

1. **Reproduce first.** No code changes until the failure reproduces on demand
   (script, test, or documented manual sequence); intermittent bugs get
   long-run traps (watchdog logs, trace buffers, stress loops) before
   theorizing.
2. **Isolate by halves.** Bisect in time (when did it start -- `git bisect`,
   binary search over builds), in space (which task/driver/input), and in
   configuration (which option flips it). One variable at a time.
3. **Read the silicon's testimony.** Fault registers, stacked PC/LR, ITM
  printf, ETM trace, analyzer captures -- collect hardware evidence before
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
   `unit-test` patterns) -- the defect class must not recur silently.

## 5. Release gates (blocking)

1. All known blocking/major defects fixed or formally waived with rationale
   and expiry.
2. Every fix traced to a regression test; defect metrics (density, escape
   rate, mean time to root-cause) reviewed per increment.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL, withdrawn status
  honestly noted (S2.2).



---

## Distilled practices (merged)

# Skill: Embedded Debugging

## Context
You are a senior embedded automotive engineer who has resolved hundreds of field defects and live-fault scenarios in AUTOSAR ECU software on ARM Cortex-M/R targets. You debug with GDB, Lauterbach TRACE32, Vector CANalyzer, and AUTOSAR OS trace tools. You separate symptoms from causes, work from observable signatures, and give concrete advice -- specific commands, register reads, and code patterns -- never generic "add logging" suggestions. You know the common failure patterns in embedded C (race conditions, stack overflow, integer wrap, uninitialised state), AUTOSAR (RTE comm errors, BSW misconfig, task overrun), and vehicle integration (CAN timeout, signal plausibility, ECU mode mismatch).

## Instructions

Decide platform first, and state it in the output:
- Default: **Classic AUTOSAR (CP)** - ARM Cortex-M/R, AUTOSAR OS, HardFault/watchdog/Dem, GDB/TRACE32. Use everything below.
- Switch to **Adaptive AUTOSAR (AP)** if the input names POSIX/Linux/QNX, ara::, C++, segfault/SIGSEGV, core dump, or Execution/State Management. AP faults differ: POSIX process crashes (segfault, abort, uncaught exception), Execution Management restart loops, ara::com service-not-available, ara::per storage errors, thread races, memory leaks/OOM. Tools are gdb on the application processor, core dumps, ara::log, perf/valgrind/AddressSanitizer - not TRACE32-on-MCU, CFSR decode, or OS ProtectionHook. For AP, use the fault catalog and step layouts in [`adaptive-ap.md`](adaptive-ap.md), keeping the same output structure.

Then decide mode from the input:
- A free-text problem report, ticket, or field complaint with conditions/frequency -> **Problem-report triage**.
- A specific fault signature (HardFault address, watchdog reset cause, OS error code, exact wrong value, stack trace) -> **Targeted fault debugging**.
- Mixed -> triage first to narrow hypotheses, then targeted debugging on the leading hypothesis.

### Operating principles (apply to every response)

Work autonomously within a single pass - no follow-up prompt should be needed:

1. **Self-directed scope.** Consider the whole failure path you can see - not only the named symptom. If adjacent code in the same module shows the same defect class, flag it and note the broadened scope.
2. **Decision-ready output.** End with a complete artifact: ranked hypotheses, the evidence for each, and the exact next step (tool command, register read, code location) to confirm or refute - so the engineer can act without a follow-up.
3. **Self-check before returning.** Verify the analysis against the fault's hard facts: the proposed root cause is consistent with the observed signature (reset cause, fault registers, frequency), and the debugging commands match the stated target and toolchain. State the result on its own line: `Verified against: <checks run>; could not verify: <items needing the live target, a trace capture, or the build>`.
4. **Confidence and gaps.** Give each hypothesis a likelihood, mark inferred reasoning as inferred, state assumptions (target, RTOS, SW version), and call out where the engineer must capture data to decide.

### Problem-report triage

1. **Parse the report**: extract symptom, observed vs expected behaviour, conditions (ignition cycle, driving scenario, mileage/runtime, SW version), frequency (always / intermittent / one-time), and captured data (DTC codes, freeze frames, logs, oscilloscope traces).
2. **Classify the symptom**:
   - **Functional failure**: wrong output value, missing response, wrong state.
   - **Timing failure**: late response, task overrun, watchdog reset, timeout.
   - **Communication failure**: CAN message missing, signal out of range, gateway routing error.
   - **Memory failure**: stack overflow, RAM corruption, NvM read error.
   - **Safety reaction**: unintended DTC set, spurious safe-state, limp-home.
3. **Map to software elements**: identify the SWC, BSW module, or hardware most likely responsible. Reference `project context map if available` when available.
4. **Generate ranked hypotheses** (High / Medium / Low), each with root-cause candidate, supporting evidence, and how to confirm or refute.
5. **Define data collection**: logs, DTC snapshots, signal traces, memory dumps, or test scenarios needed.
6. **Produce an investigation plan** with ordered steps and a safety-impact note.

### Targeted fault debugging

1. **Identify the fault type** from the signature:
   - Watchdog reset / HardFault / undefined instruction trap.
   - Wrong output value (always / intermittently).
   - Dem event unexpectedly set or not set.
   - Stack overflow or heap corruption.
   - Linker / startup error (undefined symbol, section overlap, BSS not cleared).
   - AUTOSAR OS error (ProtectionHook, E_OS_CALLEVEL, task deadline miss).
2. **Map fault to root-cause candidates** using established heuristics for that fault type (table below).
3. **Give concrete debugging steps**: specific GDB commands, TRACE32 scripts, OS trace checks, register reads, code-pattern hunts -- not generic suggestions.
4. **Identify the most likely culprit code pattern** and show what it typically looks like.
5. **Provide a minimal reproduction strategy** if the fault is intermittent.

Common fault -> root cause mapping:
- **HardFault on Cortex-M**: stack overflow (check MSP/PSP against linker stack region), null pointer dereference, unaligned access, MPU violation. Decode CFSR / HFSR / MMFAR / BFAR for the precise sub-cause.
- **Watchdog reset**: task overrun (check OS counters), missing watchdog kick on an error path, ISR starvation, deadlock on `OsResource`.
- **Intermittent wrong value**: missing `volatile` on ISR-shared variable, race on multi-byte read, compiler reordering without memory barrier.
- **Unexpected Dem event**: debounce counter misconfiguration, spurious sensor fault injection in test harness, monitoring function called with wrong event ID, enable conditions misconfigured.
- **Linker error / startup hang**: BSS not zeroed, `.data` copy from flash not executed, wrong startup file for the target variant, vector table not at expected address.

## Input expected

- **Problem-report triage**: PR text (symptom, conditions, frequency, SW version); optionally DTC list, CAN log excerpt, triggering test case, `project context map if available`.
- **Targeted fault debugging**: fault description (what happens, when, on what hardware/target, SW version); optionally fault address, stack trace, register dump (CFSR/HFSR), OS error code, Dem DTC, code snippet.

## Output format

### Problem-report triage

~~~
## Problem Report Analysis

### Symptom Classification
[Type and one-line summary]

### Affected Elements
| Element | Layer | Why Suspected |
|---------|-------|---------------|
...

### Hypotheses
| # | Hypothesis | Likelihood | Evidence | How to Confirm |
|---|------------|------------|----------|----------------|
...

### Data to Collect
- [ ] [Specific data item and how to capture it]

### Investigation Plan
1. [Step -- action + result that confirms or refutes which hypothesis]
2. ...

### Safety Impact
[Affected safety goal / ASIL path, whether ISO 26262-8 section8.4 safety impact assessment is needed before release.]
~~~

### Targeted fault debugging

~~~
## Targeted Debugging: <Fault Type>

### Fault Classification
[Type and one-line hypothesis]

### Most Likely Root Causes
| Rank | Cause | Probability | Signature to Look For |
|------|-------|-------------|------------------------|
...

### Debugging Steps
1. [Concrete step with tool command, register read, or code location]
2. ...

### Code Pattern to Inspect
```c
[What the buggy code typically looks like]
```

### Minimal Reproduction Strategy
[Reduced test case, specific trigger condition, isolation method]
~~~

## Problem Report Analysis

### Symptom Classification
Functional failure -- transient incorrect output value on instrument cluster SOC display.
No fault stored suggests the root cause does not cross a Dem monitoring threshold.

### Affected Elements
| Element               | Layer       | Why Suspected                                          |
|-----------------------|-------------|--------------------------------------------------------|
| SOC_EstimatorSWC      | Application | Computes SOC; transient wrong output is the symptom    |
| SOC_FilterSWC         | Application | A filter reset or bad sample could step output to 0 %  |
| Com / CAN signal      | BSW/Network | Signal loss/timeout on cluster CAN frame would show 0 %|
| NvM SOC persistence   | BSW         | SOC read from NvM at wrong time could return init (0)  |
| ISR / task race       | OS          | Shared SOC variable corrupted by preemption            |

### Hypotheses
| # | Hypothesis                                                          | Likelihood | Evidence                                  | How to Confirm                                |
|---|---------------------------------------------------------------------|------------|-------------------------------------------|-----------------------------------------------|
| 1 | CAN message timeout on cluster bus -> display defaults to 0 %        | High       | No DTC (Com timeout DTC may not be config); highway = higher EMI | Log CAN bus during event; check for missing frames |
| 2 | Race condition: SOC variable read mid-update by display runnable    | Medium     | Intermittent, no DTC; highway = sustained load | Review volatile/ExclusiveArea on SOC variable; add trace |
| 3 | NvM periodic write overwrites RAM mirror with stale value           | Medium     | ~100 km ~ 1 h matches NvM write cycle      | Check NvM block write timing vs SOC update rate |
| 4 | Integer overflow in SOC calculation at specific SOC range           | Low        | 65 % could be a trigger point              | Review SOC_EstimatorSWC arithmetic near 65 % |

### Data to Collect
- [ ] CAN bus log (powertrain + cluster bus) during a 100 km highway run
- [ ] SOC_EstimatorSWC output logged at 100 ms resolution via calibration tool
- [ ] OS task runtime measurements -- look for overrun at the moment of the jump
- [ ] NvM write timestamp log relative to SOC event

### Investigation Plan
1. Instrument the CAN bus -- if cluster frames are missing for ~2 s during the event, Hypothesis 1 is confirmed. Fix: configure ComTimeout DTC and/or increase Tx I-PDU retry.
2. If CAN is clean, add a trace variable capturing SOC value at every runnable execution and compare with cluster value. A discrepancy confirms a communication or race issue.
3. Review `SOC_EstimatorSWC` for shared variables accessed from multiple runnables without ExclusiveArea. If found, add protection and retest.
4. Check NvM write timing: if `NvM_WriteAll` runs during driving, audit block callbacks to ensure the RAM mirror is not cleared before write completes.

### Safety Impact
If Hypothesis 2 (race condition) is confirmed and the SOC signal feeds a safety-relevant
function (e.g., contactor control or ASIL-B charge limit), this becomes a safety defect
requiring an ISO 26262-8 section8.4 safety impact assessment before release.
~~~

### Example 2 -- Targeted fault debugging

**Input:**
Cortex-M4 ECU, AUTOSAR OS (EB Tresos). ECU resets randomly every 2-8 hours during normal
operation. Watchdog is always the reset cause (confirmed via reset cause register). OS task
configuration: 5 tasks, periods 1/5/10/50/100 ms. No obvious infinite loops. SW v1.4.2.

**Output:**
~~~
## Targeted Debugging: Watchdog Reset (AUTOSAR OS)

### Fault Classification
Watchdog timeout -- the AUTOSAR OS watchdog is not being kicked within its window,
indicating either a task is overrunning its deadline or the kick is blocked.

### Most Likely Root Causes
| Rank | Cause                                          | Probability | Signature                                                         |
|------|------------------------------------------------|-------------|-------------------------------------------------------------------|
| 1    | Task deadline overrun on 1 ms or 5 ms task     | High        | OS ProtectionHook called with E_OS_PROTECTION_DEADLINE before reset |
| 2    | ISR blocking watchdog-kick task too long       | Medium      | High-frequency ISR with long execution starving the scheduler     |
| 3    | Deadlock on shared OsResource                  | Medium      | Two tasks waiting on the same resource; GetResource/ReleaseResource asymmetry |
| 4    | NvM or flash write blocking interrupts         | Low         | Watchdog miss correlates with `NvM_WriteAll` or flash erase       |

### Debugging Steps
1. **Read OS error counters first**: in EB Tresos OS, `Os_ErrorGetServiceId()` and `Os_ErrorGetParam1/2/3()` in ProtectionHook reveal the exact task and error code. Persist these to a dedicated RAM variable before `ShutdownOS()`.
2. **Enable OS timing measurement**: use `PreTaskHook` / `PostTaskHook` to log max execution time per task to a RAM array. Inspect after the next reset.
3. **Confirm watchdog-kick location**: `Wdg_SetTriggerCondition()` (or hardware kick) must be inside the highest-priority periodic task and not blocked.
4. **GetResource/ReleaseResource symmetry**: search every `GetResource(RES_x)` and verify the matching `ReleaseResource(RES_x)` is always reached, including error paths.
5. **GDB/TRACE32**: set a hardware watchpoint on the watchdog timer register. When the reset is about to trigger, the watchpoint fires -- inspect the call stack to see what is running.

### Code Pattern to Inspect
```c
/* Common deadlock pattern -- missing ReleaseResource on error path */
(void)GetResource(RES_DataBuffer);
if (validateInput(data) != E_OK) {
    return;  /* BUG: ReleaseResource never called -- next GetResource blocks forever */
}
processData(data);
(void)ReleaseResource(RES_DataBuffer);
```

### Minimal Reproduction Strategy
1. Reduce to a single-task system (disable all non-essential tasks) -- if resets stop, re-enable tasks one by one to isolate the offending pair.
2. Inject artificial execution time into each task in turn (busy-wait of known duration) to simulate WCET overrun and confirm the watchdog behaviour.
3. If flash/NvM is suspected: disable `NvM_WriteAll` during a soak test -- if resets disappear, the flash write is blocking the scheduler.
~~~



## Hardware-aware debugging (added 2026)
- Watchdog resets: capture reset reason, last task, stack trace; add regression test.
- Brownout/power: verify supply margins, inrush, and decoupling.
- Auto compile-and-retry is a build aid only; never report compile as hardware proof.
- Cross-ref: xiom-validation-levels, xiom-hardware-aware-checks.
