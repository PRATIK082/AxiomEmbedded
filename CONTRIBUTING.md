# Contributing

1. Prefer a small, composable change over broad generated scaffolding.
2. Every new capability needs a machine-readable manifest and a deterministic test or validation case.
3. Separate domain knowledge from core engine behavior.
4. Do not copy proprietary standards text. Store identifiers, applicability metadata, mappings and project-authored interpretations only.
5. Changes affecting agents, tools, permissions, schemas or evidence must include regression coverage.
6. Use pull requests and record architectural decisions.

## Merge gate (self-handled)

Every PR touching `skills/`, `agents/`, `registries/`, client mirrors, or
`packages/skills/*` must be green on:

- `python scripts/skill_pipeline.py --check` (link→enrich→index→clients→validate)
- `python -m pytest -q`
- `python -m axiom_cli doctor`

Install the pre-commit hook once (`pip install pre-commit && pre-commit
install`) so the gate runs locally before every commit. The `nightly-drift`
workflow re-runs the same checks on schedule to catch drift that bypasses
PRs. If the gate is red, run `axiom skills apply` and re-push — never
hand-edit generated files (`registries/*.json`, `.opencode/skills/*`,
`.claude/skills/*`, `GEMINI.md`, `copilot-instructions.md`).
