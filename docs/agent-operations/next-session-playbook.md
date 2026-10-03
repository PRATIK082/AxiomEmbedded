# Next-session AI/CLI playbook

Start every new coding-agent session at the repository root.

```bash
python -m axiom_cli doctor
python -m axiom_cli repo validate
```

Then state the task in one sentence. Ask the agent to:

1. identify the active profile and workflow;
2. use `axiom analyze`/index data when a repository is new or changed substantially;
3. use graph/context selection before opening broad source trees;
4. compute impact before changing shared interfaces;
5. implement the smallest change;
6. run focused tests, static checks and applicable gates;
7. update evidence, traceability and documentation;
8. show the diff and verification result before commit/PR.

## Defect example

```text
Fix BUG-123 in the CAN receive path. Use graph-first context, recover the affected requirements/tests, implement the smallest fix, add regression coverage, run focused verification, update evidence, and stop before push.
```

## Feature example

```text
Implement FEATURE-22 for the telemetry interface. Start from the active profile, determine lifecycle entry, perform change impact, update architecture/contracts, implement, test, document and prepare a reviewable diff.
```

## Brownfield example

```text
Onboard this legacy C repository. Build the index, recover the architecture/dependencies/test baseline, report gaps, and do not modify product code until the baseline is reviewable.
```
