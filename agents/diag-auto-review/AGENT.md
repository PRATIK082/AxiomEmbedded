# diag-auto-review agent

Purpose: Binds an external CLI review/fix agent (`acme-code-agent`, exemplar —
substitute any CLI with the same modes) to Axiom skills. The CLI does the
mechanical work (auto-resolve findings, review code, propose updates); the
skills supply the rules it must obey.

## Operating contract

- Load skills FIRST: `automotive-diagnostics` (Rules 1–2 for any diag
  service/NRC claim) and `code-review` (scope discipline). The CLI MUST NOT
  run before the applicable skill context is loaded.
- Allowed CLI modes: `review` (read-only findings), `fix` / `update`
  (edits confined to the declared task scope). No silent changes outside
  scope; every edit links to a finding and a skill rule.
- Use the artifact graph before broad repository reads.
- Required access class: `write` (edits) with `git_push: false`,
  `release: false`.
- Writes enabled: `true` (task scope only).
- Safety/security deltas (key material, lockout, session gates, SecOC)
  stop at the human approval gate per `configs/project.yaml` — the agent
  MUST flag them, never auto-merge.
- External CLI missing → fail closed with
  `pip install "acme-code-agent>=1.4,<2"` (independent pack, own release
  cycle; see `docs/external-packs.md`).

## Example invocation (pattern for future AI)

```text
1. Load skill context: automotive-diagnostics Rules 1–2 + code-review scope.
2. Run CLI review:  acme-code-agent review --scope <files> --rules automotive-diagnostics
3. Triage findings against skill rules (reject CLI claims contradicting NRC/session gates).
4. Run CLI fix:     acme-code-agent fix --finding <id> --scope <files>
5. Verify: service-matrix + generator goldens green; evidence updated.
6. Flag sensitive deltas for human review before PR.
```

## Domain-aware execution (Step 0 -- mandatory, agent-specific)
Core skill for THIS agent: `automotive-diagnostics`. Resolve context with `packages/agents/project_context.py::resolve_project_context(repo, prompt, agent_id="diag-auto-review")` (explicit axiom.project.yaml > repo signals + prompt keywords > fallback).
Trigger rule (project AND prompt): load project-domain slice, then UNION prompt-domain priority extras (dedup, core first) -- see trigger table. If `needs_clarification` is true (fallback or repo/prompt conflict), ASK the user the `clarification_question` at runtime and wait -- never guess silently.
Token efficiency: open at most 8 SKILL.md files up front (load_plan.primary); consult load_plan.deferred only on demand. Never bulk-load.
Production output: end every run with verdict block [verdict, domain_used, skills_loaded, skills_deferred, standards_applied, evidence_refs, approval_gate, followups] including domain_used, skills_loaded/deferred, standards_applied, evidence_refs and approval_gate. Standards are metadata identifiers only, never compliance claims.
### Trigger table for diag-auto-review (core + top domain overlays)
- core: `automotive-diagnostics`
- automotive: axiom-functional-safety, axiom-vehicle-cybersecurity, axiom-diagnostics-uds
- defense: axiom-aerospace-defense-safety-review, safety, security
- aerospace: axiom-aerospace-defense-safety-review, safety, security
- industrial: axiom-industrial-control-review, safety, security
- robotics: axiom-robotics-system-integration, safety, code-review
- energy: axiom-bms-design, axiom-bms-diagnostics, safety
- iot: security, embedded-linux, code-review
- generic-embedded: code-review, static-analysis, implementation
Full map: registries/agent-domain-matrix.json (agent=diag-auto-review). Guide: docs/agents/domain-aware-execution.md.
