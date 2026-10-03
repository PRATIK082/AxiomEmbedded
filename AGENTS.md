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

**Discover → Plan → Select context → Change → Verify → Evidence → Review → Commit/PR.**

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

## Git rules

Agents may create branches and local commits only when explicitly permitted by the active client configuration. Pushing, merging, releasing, or changing protected branches requires human approval.
