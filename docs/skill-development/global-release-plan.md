# AxiomEmbedded Global Release Plan

**Status:** Plan (user-handled deployment). **Branch:** `feat/skill-ecosystem-strengthening`. **Skills:** 259 (197 `axiom-*`). **License:** Apache-2.0.

All content in this repository is original. No third-party skill text, code, or reference links are included. Release steps below are self-contained for this repository only.

---

## Part A — Sub-skill update workflow (repeatable, machine-gated)

### A.1 Branch & state machine
Use `workflows/embedded-skills-deep-update.yaml` (states: request → audit → research → plan → implement → verify → evidence → review → pr). One branch per skill:

```
git checkout -b chore/skill-<id>-deep-update
```

### A.2 The 8-step pipeline
1. **Audit** — `python -m axiom_cli skills validate --id <id>` + `python scripts/audit_skills.py`.
2. **Research** — skill-researcher agent (read-only) gathers authoritative sources; record concepts only, no copied text.
3. **Plan** — write delta plan; destructive ops use Plan→Validate→Execute (`plan.json` validated before `--apply`).
4. **Implement** — edit SKILL.md + manifest.yaml + checklists + templates + scripts + tests; bump version in both frontmatter and manifest.
5. **Link** — maintain `related_skills` / `sub_skills` / `extends` / `domain_overlays` / `platform_overlays` via `axiom skills link` (auto back-links).
6. **Verify** — pipeline --check, pytest, doctor, repo validate, compileall.
7. **Evidence** — run manifest under `.axiom/runs/<timestamp>/<skill-id>/`.
8. **Review & PR** — approval gate for `safety_critical: true` / `risk_level: high`; never bypass a gate.

### A.3 Sub-skill creation
- Parent declares `sub_skills`; child declares `extends` or `related_skills`.
- Use `scripts/create_skill.py` scaffold (dry-run first, then `--apply`); auto-registers catalog + facet parity.
- Each sub-skill ships: SKILL.md, manifest.yaml, checklists/, tests/ (≥3 evals for production), scripts/validate.py.

### A.4 CI gate
```bash
python scripts/skill_pipeline.py --check
python -m pytest -q
python -m axiom_cli doctor
```
Pre-commit hook runs locally; nightly drift workflow re-runs on schedule.

---

## Part B — Curated skill additions (suitable for this product)

Only skills that fit the embedded/edge/cyber-physical domain, cross-domain, cross-skill, and bi-directional use cases are added. No third-party skill is copied; all are independently authored. Candidate capability areas (already scaffolded where marked):

- Cloud/edge platform: cloud-architecture, kubernetes-edge, terraform-infra, monitoring-observability, sre-reliability.
- Resilience: chaos-engineering.
- Tooling: cli-developer, mcp-developer.
- Edge AI / data: prompt-engineering, rag-architect, data-pipeline, database-optimization.
- Integration: api-design, graphql-architect, microservices-architect, websocket-engineer.
- Quality: test-master, playwright-e2e, debugging-wizard, legacy-modernizer.
- Security: secure-code-guardian, security-reviewer.
- Meta: skill-evolution (self-improving skill loop, original implementation).

Each addition follows Part A.2 end-to-end before merge.

---

## Part C — Global release (user-handled)

### C.1 Pre-release checklist
- [ ] Clean working tree on release branch; regenerated derived files (`axiom skills apply`).
- [ ] `python scripts/skill_pipeline.py --check` → OK.
- [ ] `python -m pytest -q` → all pass.
- [ ] `python -m axiom_cli doctor` → repo PASS.
- [ ] `python -m axiom_cli repo validate` → PASS.
- [ ] `python -m compileall -q axiom_cli packages scripts` → clean.
- [ ] Secret/vuln scan (no committed secrets).
- [ ] LICENSE (Apache-2.0) + NOTICE present.
- [ ] README.md updated with install + quickstart + skill count + badges.
- [ ] CHANGELOG.md with semver entries.
- [ ] Version bump in `configs/project.yaml` + pyproject.toml + catalog.

### C.2 Git / GitHub
1. Push branch: `git push -u origin feat/skill-ecosystem-strengthening`.
2. Open PR against `main` (approval gate for merge).
3. Merge after CI green; tag release: `git tag -a v1.3.0 -m "..." && git push origin v1.3.0`.
4. Keep repository public for discoverability.

### C.3 Package publishing
- Build: `python -m build`; publish: `python -m twine upload dist/*`.
- End users: `pip install axiom-cli` then `axiom skills list`.
- Pre-check: `python -m twine check dist/*`.

### C.4 MCP server listing
- Submit the Axiom MCP server (`axiom_mcp/server.py`, 39 tools) to the MCP server registry via PR.
- Config in `.mcp.json` (tracked generated file).

### C.5 CI/CD for releases
- `.github/workflows/release.yml`: on tag `v*` → build → publish → GitHub Release.
- `.github/workflows/nightly-drift.yml`: runs pipeline --check, pytest, doctor.

### C.6 Documentation deliverables
- README.md, CONTRIBUTING.md (merge gate documented), SECURITY.md, CODE_OF_CONDUCT.md (optional).

### C.7 Versioning
- Semver: target v1.3.0 (or 2.0.0 if breaking CLI changes). Tag format `v1.3.0`.

### C.8 Post-release monitoring
- Track GitHub stars/issues, install counts, downloads.
- Autonomy KPI: human-intervention count, gate pass rate, eval success rate, token cost per artifact.

---

## Follow-ups not yet implemented
- Eval harness `packages/eval/`.
- Autonomy KPI dashboard.
- Rule files for hardware-aware checks.
- Profiles for embedded peripherals.
- EV-embedded evaluation tasks.
- Cloud/data/ML/web/mobile/observability domains (partial).

## Identity / git
- Author: PRATIK082 <pratik.patil082@gmail.com>.
- Branches: `feat/embedded-skills-intelligence-initiative` (pushed), `feat/skill-ecosystem-strengthening` (pushed, `4629bd4`).
- No remote push of main/tag performed; user handles all releases above.
