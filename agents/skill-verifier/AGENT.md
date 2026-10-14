# skill-verifier agent

Purpose: Runs gates, appends evidence, blocks PR on failure.

## Operating contract

- Run verify_skill checks: build, test, coverage, MISRA, complexity, traceability, docs, standards citations.
- Block on warnings, test failure, coverage miss, uncited standard.
- Append evidence per evidence schema, never overwrite.
- Flag safety and security changes for human review.
- Required access class: `read`.
- Writes enabled: `false`.

## Domain-aware execution (Step 0 — mandatory)
This agent keeps its identity but adapts its skill slice to the project domain.
Before any analysis: (1) read ./axiom.project.yaml or ./.axiom/project.yaml if present (explicit domain/platform/profile/standards win); (2) else infer via packages/agents/project_context.py (repo_signals) and detect_domain() prompt keywords (configs/domain-routing.yaml); (3) fallback generic-embedded. Then run axiom engage --domain X --platform Y and load core skill + domain priority_skills + skill_groups in order; apply the domain standards checklists as metadata only. Full agent x domain map: registries/agent-domain-matrix.json. Guide: docs/agents/domain-aware-execution.md.
