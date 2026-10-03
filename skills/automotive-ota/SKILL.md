---
name: automotive-ota
description: SOTA/FOTA campaigns per UNECE R156/SUMS, A/B + delta updates, UCM, rollback, backend-to-vehicle chain. Use for updateable fleets or type-approval evidence.
version: 1.2.0
domains: [automotive]
platforms: [mcu, mpu, autosar-classic, autosar-adaptive]
---

# automotive-ota — Software update and campaign capability

Reusable AxiomEmbedded capability for backend-to-vehicle software updates: Software Update
Management System (SUMS) per UNECE R156, SOTA/FOTA campaign management, A/B plus delta
packaging, Update-and-Config-Management (UCM) behaviour, rollback discipline, and the
bootloader-anchored vehicle trust chain.

## Objectives

- Stand up an R156-recognisable SUMS: version control, update integrity, dependency/
  compatibility checks, rollback, audit trail.
- Deliver A/B (slot) plus delta update packages with atomic activation.
- Define UCM behaviour (transfer, verify, install, activate, rollback, status reporting).
- Run campaigns: eligibility, rollout waves, consent, safe-state gating, retry/resume,
  backend-to-vehicle evidence chain.
- Anchor every update in the bootloader trust chain (`skills/bootloader/`,
  `skills/automotive-diagnostics/` FBL path).

## Prerequisites

- Bootloader with verify-before-jump, trial/permanent slots, anti-rollback
  (`skills/bootloader/`); diagnostics/FBL path where UDS programming is used.
- Connectivity bearer via `skills/automotive-networks/`; key/certificate custody defined.
- Baselines recorded (verify before citing): UNECE R156 (SUMS), ISO 24089 (software-update
  engineering), AUTOSAR Adaptive UCM, ISO/SAE 21434 (update threat linkage).
- Domain overlay loaded: `domains/automotive/` (mandatory).

## Outcomes

- `requirements/ota-requirements.md`: SUMS obligations, package types, compatibility matrix,
  rollback/safe-state/consent requirements.
- `architecture/ota-architecture.md`: backend → connectivity → UCM → bootloader data flow,
  key/verification points, campaign states.
- `packages/` signed delta/full images with manifest + UCM adapter.
- `test/` package-verification, install/rollback, campaign-simulation, power-loss, backend-chain tests.
- `evidence/` SUMS-traceable update records per campaign.

## Time estimate

- SUMS + package/UCM design: 3–5 days. Campaign pipeline + backend stub: 5–8 days.
  Rollback/power-loss/campaign hardening: 3–5 days.

## Resources (public landing pages only)

- UNECE WP.29: `https://unece.org/transport/vehicle-regulations`
- ISO 24089: `https://www.iso.org/search.html?q=24089`
- ISO 14229 (FBL context): `https://www.iso.org/search.html?q=14229`
- ISO 13400 (DoIP bearer): `https://www.iso.org/search.html?q=13400`
- ASAM overview: `https://www.asam.net/standards/`
- AUTOSAR Adaptive (UCM): `https://www.autosar.org/standards/adaptive-platform`
- OPEN Alliance: `https://www.opensig.org/`

## Rule 1 — OTA state machine (normative for this skill)

```text
Idle → Eligible → Downloaded → Verified → Staged
  → InstallGated(safe-state+consent) → Installing
  → TrialBoot → Confirmed | RolledBack
Confirmed → Idle (report). Any failure → Failed(safe prior image) → Idle.
```

1. Advance only on recorded guard: eligibility (VIN/variant/version/dependency match),
   integrity (hash + signature), safe-state (parked/speed/power interlock), consent where required.
2. `TrialBoot` is mandatory: new image runs self-test before `Confirmed`; unconfirmed images
   never survive the next reset.
3. `RolledBack` restores the prior confirmed image and emits an auditable event with reason
   code; silent fallback is forbidden.
4. Backend status mirrors vehicle truth; divergent reports block campaign closure.

## Rule 2 — Package rules (A/B + delta)

1. **A/B discipline:** inactive slot written, verified, then atomically activated; single-slot
   targets use bootloader swap/scratch with the same trial/confirm semantics.
2. **Delta discipline:** base-version pinned in manifest; delta applies only to exact base hash;
   reconstruction hash must equal full-image hash before activation. Fallback to full image on mismatch.
3. **Manifest minimum:** target ECU(s), from/to versions, dependencies, size, hashes, signatures,
   anti-rollback counter. Unsigned or counter-regressed packages rejected closed with an event.
4. **Transport integrity:** resume-capable transfer with per-chunk checks; end-to-end signature
   verified on-vehicle, not only in backend.

## Rule 3 — UCM behaviour contract

1. Transfer → verify → install → activate → rollback/status, each step individually reportable;
   a step is never skipped by configuration.
2. Concurrent-update policy explicit: parallel vs sequence, gateway/battery/network-load constraints.
3. Version reporting (R156-recognisable): every ECU reports type-approval-relevant versions on
   request; backend records match vehicle reports.
4. Configuration (where UCM-managed): parameter sets versioned with their software; partial config
   without its software is rejected.

## Rule 4 — Campaign and backend-to-vehicle chain

1. Waves: canary → expanded → full, with halt/rollback criteria defined before wave one.
   No campaign without a stop rule.
2. Eligibility computed server-side and re-checked vehicle-side; both decisions logged.
   Mismatch → hold, investigate, do not force.
3. Backend→vehicle chain: build-sign → publish → distribute → vehicle verify → install →
   confirm → report, each handover signed/logged so the chain is replayable in an audit.
4. Consent and safe-state gating are requirements with tests, including "consent withdrawn
   mid-download" and "safe-state lost mid-install" cases.

## Integration and test strategy

- Package tests: tampered payload, wrong base-version delta, regressed counter,
  truncated transfer/resume — all rejected with reason codes.
- Vehicle tests: full download→trial→confirm and every abort edge, each ending on a
  bootable confirmed image.
- Power-loss matrix (with `skills/bootloader/`): cut at download, verify, stage, install,
  trial, confirm, rollback — each boots to a working image with correct status report.
- Campaign simulation: eligibility mismatch, wave halt, backend/vehicle divergence,
  fleet-scale reconciliation.
- Security tests: key-rotation acceptance, revoked-key rejection, replay of older campaign
  package (must fail closed).

## Traceability

- SUMS obligation → requirement → package manifest → UCM step → vehicle test → campaign
  record → evidence id. Standards cited as number + version + identifier only.

## Compliance mapping (via overlays, not duplication)

- UNECE R156 (SUMS) as approval-facing frame; UNECE R155 / ISO/SAE 21434 for update-threat
  linkage; ISO 26262:2018 where updates touch safety functions. Never claim type approval
  or homologation from this heuristic skill.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill automotive-ota` → PASS.
2. State-machine coverage: every transition and abort edge tested.
3. Delta + full packages proven; wrong-base and regressed-counter rejected with events.
4. Trial/confirm/rollback demonstrated on hardware with power-loss cuts.
5. Campaign stop rules defined; halt and divergence cases tested.
6. Backend→vehicle chain replayable from signed records.
7. Traceability complete; no copied normative text.
8. Safety/security deltas flagged for human review before PR.

Load task-specific domain/platform/rule overlays before execution.
