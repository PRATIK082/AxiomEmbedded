---
name: axiom-validation-orchestrator
title: Cross-Layer Validation Orchestrator
description: >
  Routes a verification target (MCU firmware, Embedded Linux image, or full
  system) to the right execution engine -- Unity/GoogleTest for unit-level C/C++,
  Pytest plus Labgrid for developer-driven integration, Robot Framework for
  system-level HIL and acceptance -- and generates the matching test skeleton
  with pre-check, execution, and triage phases. Use when starting any SIL, HIL,
  or system validation campaign that spans more than one testing layer.
version: 1.2.0
author: AxiomEmbedded
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.validation.orchestrator
  domain: all
  maturity: experimental
  safety_critical: false
  activity: validation
  capability_kind: validator
  primary_domain: all
  risk_class: medium
  inputs: [repository path, test target, test objective, constraints]
  outputs: [engine selection, test skeleton, run report, run manifest]
  required_tools: [run_skill]
  optional_tools: [validate_skill]
  lifecycle: [plan, implement, verify, evidence]
  standards: []
  artifact_types: [validation plan, test skeleton, evidence package]
  mcp_tools: [run_skill, validate_skill]
  risk_level: medium
  review_required: true
  related_skills: []
---
# Cross-Layer Validation Orchestrator

## Purpose

Select the right test execution engine for the target under test and emit a
runnable skeleton wired for pre-check, execution, and triage. This is the
meta-skill for the V&V framework: it never executes tests itself, it routes
(unit to Unity/GoogleTest, integration to Pytest/Labgrid, system/HIL to Robot
Framework) and chains the sibling skills (`axiom-hw-interface-control`,
`axiom-bus-protocol-validation`, `axiom-firmware-lifecycle`,
`axiom-sil-hil-bridge`) into one campaign.

## When to Use

- The test target spans more than one layer (unit plus integration, SIL plus HIL).
- A new campaign needs a skeleton, engine choice, and evidence layout.
- Inputs below are available.

## When Not to Use

- As a substitute for qualified safety/security certification review.
- When required inputs are absent (record the gap instead of inventing data).

## Required Inputs

- Repository path and test target files.
- Test objective, target description (MCU firmware, Linux image, full system).
- Constraints (bench availability, simulator licenses, time budget).

## Optional Inputs

- Existing test plans, prior skeletons, bench inventory (`board_config.yaml`).

## Prerequisites

- `axiom doctor --skip-tests` green.
- Target builds reproducibly (`axiom-firmware-lifecycle` flash path known).

## Execution Workflow

1. Normalize the request into objective, target kind, scope, and constraints.
2. Classify the target: MCU firmware, Embedded Linux image, or full system.
3. Select engine(s) per layer using the Decision Rules table.
4. Generate the skeleton (dry-run first): engine project layout plus
   pre-check/execution/triage hooks.
5. Chain sibling skills: flash via `axiom-firmware-lifecycle`, stimulate via
   `axiom-hw-interface-control`, parse via `axiom-bus-protocol-validation`,
   promote SIL cases via `axiom-sil-hil-bridge`.
6. Validate structurally (scripts/ plus checklists/).
7. Record assumptions, risks, and next actions in the run manifest.

## Decision Rules

| Target layer | Engine | Simulator first | HIL promotion |
|---|---|---|---|
| Unit / low-level C/C++ firmware | Unity or GoogleTest | QEMU/Renode or on-target JTAG/SWD | Same assertions, timing tolerances widened |
| Developer integration / Embedded Linux | Pytest plus Labgrid | Containers, virtual DUT | Labgrid physical DUT, board state mgmt |
| System-level, HIL, cross-functional acceptance | Robot Framework | Plant model SIL | Physical HIL rig, domain keywords |

- Prefer explicit configuration over invented defaults; flag every assumption.
- Pre-check (bench readiness: instrument ping, DUT power rails, firmware hash)
  runs before any execution phase.
- Safety/security-relevant outputs require human review (`review_required: true`).

## Tool Invocations

- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.

## Workflow

Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables

- Engine selection with rationale, test skeleton, validation plan mapping
  requirements to layers.

## Acceptance Criteria

- `validate_skill` passes; checklist gates all green; traceability complete.
- Skeleton references logical bench names only (see `axiom-hw-interface-control`
  `board_config.yaml`); no hardcoded IPs, ports, or VISA strings.
- Triage phase defined (diagnostic bundle plus root-cause classification).

## Acceptance

- All checklist gates pass; findings carry severity plus evidence plus action.

## Validation Procedure

1. `python skills/axiom-validation-orchestrator/scripts/validate.py`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes

- Hardcoded bench addresses in generated skeletons -> reject; use logical names.
- Skipping pre-check and running against a dead bench -> block execution.
- Reporting SIL pass as HIL proof -> explicitly forbidden.

## Guardrails

- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## Self-Direct Team Mode

Any AI module, CLI, or plugin with AxiomEmbedded MCP access must derive the
same campaign a human team would: analyze first, then plan, then execute.

1. Analyze repo state: enumerate targets (firmware dirs, Linux images, system
   composition), existing tests per layer, bench inventory, prior reports.
2. Derive the objective backlog: untested layers, uncovered buses, missing
   fault cases, open findings from prior runs. Rank by risk (safety-relevant
   and security-exposed first).
3. Emit a role plan that mirrors a product team: Planner (scope plus engine
   selection), Executor (skeleton plus run), Triage (bundle plus classify).
   One agent may play all roles in sequence; the role outputs stay separate
   artifacts so a team of agents can split them without overlap.
4. Execute in layer order (unit, integration, system) with pre-check gates;
   stop the line on bench-unready, never route around it.
5. Report like a company build review: verdict per objective, evidence links,
   residual risks, next backlog.

Missing inputs become explicit questions recorded in the manifest, never
silent guesses. Two different harnesses running this skill on the same repo
must converge on the same engine selection and backlog ordering.

## Failure-Case Analysis Mandate

Every validation plan contains positive, negative, and fault triplets per
requirement: the nominal pass, the boundary rejection, and the injected
failure with its expected fail-safe. System-failure cases are mandatory
where applicable: power loss mid-flash, bus-off storms, watchdog starvation,
brownout during update, sensor freeze plus plausible drift. Each fault case
declares the expected safe state before injection; a fault without a
declared expectation is rejected at review.

## Engine Selection Matrix (Extended)

| Objective | Engine | Pattern |
|---|---|---|
| C unit with hardware mocks | Ceedling (Unity plus CMock) | layered firmware with hardware stand-ins; generated mocks and runners |
| On-target unit plus integration | pytest-embedded class runner | same test code on host and target; CI flashes then runs |
| Developer integration, Embedded Linux | Pytest plus Labgrid | places bind boards; fixtures own power and console |
| Security pass (static, CVE, fuzz) | static analysis plus CVE correlation plus grey-box fuzzing with automated report | findings triaged into blocker, major, minor buckets |
| Update-fault pass | Renode-driven fault injection over storage, CPU, bus, OTP paths with recovery plus security postconditions | corrupt, truncate, and power-cut images must reject and recover |
| System, HIL, acceptance | Robot Framework (default) | keyword suites below; virtual ECU behind an API for SIL, physical rig for HIL |

## Robot Framework Keyword Architecture

Follow the proven HIL-suite shape: thin keywords over Python driver
libraries, resource files per bench (`bench_keywords.resource`), variable files
per board (generated from `board_config.yaml` logical names), and test
suites per requirement area. The same suite runs harness-less against a
virtual ECU API in SIL and against the physical rig in HIL; only the
variable file and timeouts change (see `axiom-sil-hil-bridge` tolerance
policy). Tag every case `sil` or `hil`, plus `security` for fuzz cases and
`no-harness` for bench-independent runs, so CI selects subsets without
editing suites.

## Boundary End-Caps

- Lower end-cap: campaign starts only with a validated `board_config.yaml`
  (or an explicit no-harness declaration) plus a hash-attested firmware
  identity. Anything less is a planning finding, not a run.
- Upper end-cap: campaign ends with a signed validation report mapping every
  requirement to positive, negative, and fault verdicts with evidence links.
- Out of scope: silicon characterization, RF compliance lab work, and formal
  certification audits. Findings that point there are handed off with data,
  not stretched into claims.

## Advanced V&V patterns (P1)

### Multi-DUT orchestration `[HIGH]`
Parameterize suites per DUT identity and channel map; synchronize multi-DUT
cases with per-device options. Required for gateway and multi-node campaigns.

### RF remote execution `[MEDIUM]`
pabot parallel runs, Rebot merge, remote servers for distributed benches;
select subsets by tags (`sil`, `hil`, `security`, `no-harness`).

### Cloud emulation for hardware-free CI `[MEDIUM]`
Wokwi/esp-emu/QEMU for SIL smoke; promotion to physical rig remains
mandatory for release claims.

### Panic/core-dump decoding `[HIGH]`
Automated backtrace decode on failure; attach decoded trace to the triage
bundle.

### Flash caching `[MEDIUM]`
Hash-based skip-reflash when the attested image is present; invalidate on
hash mismatch or policy change.

### Firmware provisioning in CI `[HIGH]`
Automated flash of attested firmware before any HIL phase; hash gated in
pre-check.

### Sanitizer gates `[HIGH]`
ASan/UBSan/LSan on host-level suites routed through Unity/GoogleTest/Pytest;
findings block merge.

## Standards rule map (copyright-safe: IDs + clauses only)

| Rule ID | Standard clause | Intent (paraphrased) |
|---|---|---|
| VO-R1 | ISO/IEC/IEEE 29119 | Test process and orchestration |
| VO-R2 | ISO 26262-6 S10 | Software integration test methods |


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

- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.
- Cross-references: `axiom-hw-interface-control`, `axiom-bus-protocol-validation`,
  `axiom-firmware-lifecycle`, `axiom-sil-hil-bridge`, `axiom-validation-levels`,
  `axiom-mil-sil-hil-testing`.
