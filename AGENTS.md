# AxiomEmbedded Agent Contract

AxiomEmbedded is a domain-neutral engineering platform. Treat this file as the repository-wide operating contract for AI coding agents.

## First-read order

1. `README.md`
2. `REPOSITORY_INVENTORY.md`
3. `docs/agents/working-agreement.md`
4. `configs/project.yaml`
5. The profile/workflow relevant to the current task
6. Only then inspect task-specific source, tests, rules and evidence.

## Context discipline

Do not preload the whole repository. Prefer `axiom_cli` graph/index/context commands and targeted file reads. For a defect or feature, identify the artifact roots first, then expand only the required dependency/traceability neighbourhood.

## Required workflow

**Discover -> Plan -> Select context -> Change -> Verify -> Evidence -> Review -> Commit/PR.**

A code change is incomplete until the appropriate verification and evidence artifacts are updated.

## Change rules

- Keep public contracts versioned and backward-compatible where practical.
- Prefer small, composable packages and plugins over cross-domain duplication.
- Keep domain knowledge in domain/profile/skill packages, not in core algorithms.
- Keep standards metadata and applicability separate from proprietary normative text.
- Never claim certification or standards compliance from a heuristic check.
- Preserve traceability for requirements, changes, tests, rules and evidence.
- Generated files must identify their generator and remain reproducible.
- Do not silently alter user code outside the declared change scope.

## Safety/security boundaries

For safety-, security- or mission-critical changes, produce an impact assessment and stop at the configured approval gate before merge/release. Never bypass a gate merely to make CI green.

## Verification

At minimum for Python changes:

```bash
python -m compileall -q axiom_cli packages scripts
python -m pytest -q
python -m axiom_cli doctor
python -m axiom_cli repo validate
```

For configuration/schema changes, also run profile and schema validation. For agent changes, run the applicable evaluation suite.

## Three-zone autonomy

Autonomy is zoned by risk. The V&V boundary is the automation boundary.

- **Core / evidence zone** (AI no access, human accountable): certified/qualified artifacts, evidence records, safety/security-critical code, release baselines. AI must not read or write here without an explicit human-approved change request.
- **Gray zone** (AI assistant + HITL): AI plans the path and drafts changes, but a human decides and approves each step. Includes architecture, requirements, tests with safety impact, and configuration affecting verification.
- **Non-critical zone** (AI unrestricted): documentation, examples, generated scaffolding, low-risk refactors, and tooling glue. AI may act autonomously, subject to review.

## Knowledge-base layering

Keep repository knowledge in distinct layers so each has one owner and one update path:

- `rules/` - enforceable rules and constraints.
- `knowledge-base/` - reference material and domain facts.
- `skills/` - procedures and how-to guidance.
- `agents/` - personas and role definitions.
- `commands/` - slash-command entry points.
- `workflows/` - end-to-end process definitions.
- `hooks/` - safety gates and automation hooks.
- `tools/` - adapters and integrations.

## Deviation management

Any deviation from a rule or standard must be recorded with: Rule ID, reason, file/location, approver, and date (Straion pattern). Deviations are tracked as first-class artifacts, not comments.

## Copyright-safe standards

Never reproduce normative standards text. Store identifiers, clause numbers, applicability metadata, mappings, and project-authored interpretations only.

## Builder + reviewer pairs

Every artifact-producing skill is paired with a confirmation reviewer that independently checks its output before acceptance.

## Self-updating meta-rule

Rules are updated when a bug fix reveals a gap. Architectural decisions (ADRs) are kept separate from lessons learned; lessons do not become ADRs without explicit review.

## Git rules

Agents may create branches and local commits only when explicitly permitted by the active client configuration. Pushing, merging, releasing, or changing protected branches requires human approval.
