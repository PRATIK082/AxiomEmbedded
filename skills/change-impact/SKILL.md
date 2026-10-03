# Change-Impact skill

Systematic analysis of proposed changes before approval: what is affected,
what must be re-verified, and what the change costs — so baselines evolve
without silent breakage.

## 1. Purpose and scope

**Purpose.** Turn "small fix" optimism into a documented impact statement with
re-verification scope, so approvers decide on facts.

**In scope.** Change requests, impact analysis method (trace-driven + expert
review), regression scoping, safety/security re-assessment triggers, and the
change record as a configuration item.

**Non-goals.** Implementing the change (owner skill) or release packaging
(see `release`, `configuration-management`).

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO 26262-8 | 2018 | Clause 8 change management: request, analysis, decision, implementation | `https://www.iso.org/standard/68390.html` |
| 2 | ISO 10007 Quality — configuration management | 2017 | Change control process, status accounting | `https://www.iso.org/standard/70400.html` |
| 3 | IEEE 1042 Configuration management | 1987 (reaffirmed) | Change classification and control board practice | `https://standards.ieee.org/ieee/1042/4257/` |

## 3. Analysis method

1. **Trace-driven blast radius.** Starting from the changed artifact, follow
   `traceability` links in both directions: upstream requirements affected,
   downstream design/code/tests/evidence invalidated (suspect links per
   `traceability` §4). The trace query is attached to the change request.
2. **Expert review for the untraced.** Timing, performance, power, and emergent
   behavior rarely trace cleanly — a reviewer from each affected discipline
   signs the "no further impact" statement explicitly.
3. **Safety/security trigger test.** Any change touching a safety-related
   requirement, safety mechanism, toolchain, or security boundary triggers
   re-assessment scoping per `safety` §6 / `security` policy — the trigger
   decision is recorded even when the answer is "no re-assessment needed."
4. **Regression scope derived, not guessed.** Re-verification list = invalidated
   tests + interface neighbors + timing re-measurement where budgets exist.
   "Full regression" is the default when the scope cannot be bounded.

## 4. Change record and gates (blocking)

The change record carries: description, rationale, blast-radius query result,
expert sign-offs, re-verification list with results, and approval. Gates:

1. Impact statement complete with trace query attached.
2. Safety/security trigger decision recorded.
3. Re-verification executed green; suspect links cleared.
4. Approval by an authority independent of the implementer for
   safety/security-relevant changes.

## 5. Verification of this skill (Phase 4 gate)

- Sample closed changes: blast radius present, re-verification matches scope.
- No safety-relevant change without a recorded trigger decision.
