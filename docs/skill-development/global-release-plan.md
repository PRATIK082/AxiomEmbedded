# AxiomEmbedded Global Release & Skill Ecosystem Plan

**Status:** Plan (user-handled links/deployment). **Branch:** `feat/skill-ecosystem-strengthening` (local, commit `1f32f89`). **Skills:** 237 (175 `axiom-*`). **License:** Apache-2.0.

This plan covers three deliverables the user will execute:

1. **Proper sub-skill update workflow** (how a sub-skill is created/updated/verified).
2. **User ability to add / link / find the best suitable skill from the internet** and integrate or support current skills.
3. **Global release** of the package (PyPI, GitHub discoverability, marketplaces, MCP, awesome lists).

---

## Part A — Sub-skill update workflow (repeatable, machine-gated)

### A.1 Branch & state machine
Use the existing deep-update workflow `workflows/embedded-skills-deep-update.yaml` (states: request → audit → research → plan → implement → verify → evidence → review → pr). One branch per skill:

```
git checkout -b chore/skill-<id>-deep-update
```

### A.2 The 8-step sub-skill update pipeline
1. **Audit** — `python -m axiom_cli skills validate --id <id>` + `python scripts/audit_skills.py` (find gaps: missing tests/, scripts/, references/, checklists).
2. **Research** — (skill-researcher agent, read-only) gather authoritative sources; record in `docs/skill-development/source-and-license-register.md` (no proprietary text).
3. **Plan** — write `skills/<id>/...` delta plan; for destructive ops use Plan→Validate→Execute (`plan.json` validated before `--apply`).
4. **Implement** — edit SKILL.md + manifest.yaml + checklists + templates + scripts + tests; bump version in **both** frontmatter and manifest (parity enforced by validator).
5. **Link** — maintain `related_skills` / `sub_skills` / `extends` / `domain_overlays` / `platform_overlays` via `axiom skills link` (auto back-links, symmetry enforced).
6. **Verify** —
   - `python scripts/skill_pipeline.py --check`
   - `python -m pytest -q`
   - `python -m axiom_cli doctor`
   - `python -m axiom_cli repo validate`
   - `python -m compileall -q axiom_cli packages scripts`
7. **Evidence** — run manifest under `.axiom/runs/<timestamp>/<skill-id>/` (report.md + run-manifest.json) via `axiom skills run <id> --apply`.
8. **Review & PR** — approval gate for `safety_critical: true` / `risk_level: high`; never bypass a gate to make CI green.

### A.3 Sub-skill creation (new child under a parent)
- Parent declares `sub_skills: [axiom-<parent>-<child>]`.
- Child declares `extends: axiom-<parent>` (or `related_skills`).
- Use `scripts/create_skill.py` scaffold (dry-run first, then `--apply`); it now registers catalog entry + facet parity (F0 fix).
- Each sub-skill ships: SKILL.md, manifest.yaml, checklists/, tests/ (≥3 eval scenarios for production), and (for production) scripts/validate.py.

### A.4 CI gate (must be green before merge)
```bash
python scripts/skill_pipeline.py --check
python -m pytest -q
python -m axiom_cli doctor
```
Pre-commit hook (`pip install pre-commit && pre-commit install`) runs this locally. Nightly drift workflow re-runs on schedule.

---

## Part B — Add / link / find best suitable skills from the internet

### B.1 Discovery sources (links the user browses)
| Source | URL | Use |
|---|---|---|
| Agent Skills spec | https://agentskills.io/specification | Canonical SKILL.md format |
| Reference impl + `skills-ref` | https://github.com/agentskills/agentskills | `skills-ref validate ./skill` |
| skills.sh (Vercel) | https://www.skills.sh | 35k+ indexed; `npx skills add owner/repo` |
| agentskill.sh | https://agentskill.sh | Universal manager, 42+ agents |
| agentskills.in marketplace | https://agentskills.in/marketplace | Ranked by stars |
| skills-hub.ai | https://skills-hub.ai | 198 synced sources, daily |
| AI Agents Directory | https://aiagentsdirectory.com/skills | 3,004 skills |
| agentcatalog.ai (SkillMill) | https://agentcatalog.ai | Security-scanned, certified |
| skillforagents.com | https://skillforagents.com | MCP + skills directory |
| Anthropic skills | https://github.com/anthropics/skills | 21 reference skills (skill-creator, mcp-builder, …) |
| OpenAI skills | https://github.com/openai/skills | 56+ curated |
| JetBrains skills | https://github.com/JetBrains/skills | Flat layout + `metadata.source` provenance pattern |
| VoltAgent awesome list | https://github.com/VoltAgent/awesome-agent-skills | Most-contributed index (200+) |
| kodustech awesome | https://github.com/kodustech/awesome-agent-skills | Software-engineering focused |
| seb1n awesome | https://github.com/seb1n/awesome-ai-agent-skills | Agent-engineering skills |
| DevelopersGlobal | https://github.com/DevelopersGlobal/ai-agent-skills | Lifecycle-organized (THINK→SHIP) |
| mattpocock/skills | https://github.com/mattpocock/skills | diagnosing-bugs, improve-codebase-architecture, … |
| ningzimu/awesome-skills | https://github.com/ningzimu/awesome-skills | Meta-skill auto-installer + Skill_Seekers |
| Skill_Seekers | https://github.com/ningzimu/Skill_Seekers (see awesome-skills) | Converts docs/GitHub/OpenAPI/PDF → SKILL.md |

### B.2 Ingestion workflow (for a candidate skill found online)
1. **Find** candidate via search/awesome lists/marketplace.
2. **License check** — confirm compatible license (Apache-2.0 / MIT preferred); record provenance in `source-and-license-register.md`. Never copy proprietary normative text.
3. **Validate upstream** — `skills-ref validate ./skill` (from agentskills/agentskills).
4. **Convert** — use Skill_Seekers to convert docs/GitHub/OpenAPI/PDF → SKILL.md, OR manually map to Axiom layout.
5. **Provenance** — add `metadata.source: <upstream-url>@<commit>` (JetBrains pattern) in SKILL.md frontmatter; map external `metadata` into Axiom `axiom:` block.
6. **Scaffold** — `python scripts/create_skill.py --id axiom-<domain>-<cap> --apply` (registers catalog + facet parity).
7. **Adapt** — add Axiom contract fields (inputs/outputs/required_tools/risk_level/review_required/safety_critical/lifecycle/related_skills/artifact_types/maturity), checklists, tests (≥3 evals), scripts/validate.py.
8. **Link** — `axiom skills link --from <new> --to <existing> --kind related_skills` (auto back-links).
9. **Verify** — full CI gate (Part A.2 step 6).
10. **Security scan** — SkillMill-style scan for secrets/vulns/dangerous patterns before publish (user-handled).

### B.3 CLI / MCP entry points the user drives
- `axiom skills create --id ... --dry-run` / `--apply`
- `axiom skills link --from ... --to ... --kind related_skills|extends|sub_skills|domain_overlays|platform_overlays`
- `axiom skills validate --id ...`
- `axiom skills run <id> --apply` (writes run manifest)
- `axiom skills apply` (regenerates derived files)
- `axiom skills search "<query>"`
- MCP tools (axiom_mcp/server.py): `create_skill`, `link_skill`, `validate_skill`, `run_skill`, `skill_pipeline`, `search_skills`, `engage`, `read_skill`.
- `python scripts/skill_pipeline.py --check` / (apply)

### B.4 "Find best suitable skill" helper (recommended new command — backlog)
Add `axiom skills discover "<query>"` that queries skills.sh/agentskill.sh search + GitHub code search and returns ranked candidates with license + provenance. (Not yet implemented; tracked as follow-up R-add.)

---

## Part C — Global release (user-handled links/deployment)

### C.1 Pre-release checklist (must all be green)
- [ ] `git status` clean on release branch; all generated files regenerated (`axiom skills apply`).
- [ ] `python scripts/skill_pipeline.py --check` → OK (237 skills).
- [ ] `python -m pytest -q` → all pass.
- [ ] `python -m axiom_cli doctor` → repo PASS.
- [ ] `python -m axiom_cli repo validate` → PASS.
- [ ] `python -m compileall -q axiom_cli packages scripts` → clean.
- [ ] `skills-ref validate` on every imported external skill (https://github.com/agentskills/agentskills).
- [ ] Secret/vuln scan (no committed secrets).
- [ ] LICENSE (Apache-2.0) + NOTICE present at repo root.
- [ ] README.md updated with install + quickstart + skill count + badges.
- [ ] CHANGELOG.md with semver entries.
- [ ] Version bump in `configs/project.yaml` + pyproject.toml + catalog.

### C.2 Git / GitHub (user handles)
1. Push branch: `git push -u origin feat/skill-ecosystem-strengthening`.
2. Open PR against `main` (never push directly to protected branch; approval gate).
3. Merge after CI green; tag release: `git tag -a v1.3.0 -m "..." && git push origin v1.3.0`.
4. Ensure repo is **public** so skills.sh indexes it (skills.sh indexes GitHub repos → discoverability).
   - https://www.skills.sh (auto-indexes public GitHub skill repos)
   - Install command for end users: `npx skills add PRATIK082/AxiomEmbedded`

### C.3 PyPI — publish the CLI (user handles)
- Build: `python -m build` (requires `pyproject.toml` with `[project] name = "axiom-cli"`).
- Publish: `python -m twine upload dist/*` → https://pypi.org
- End users: `pip install axiom-cli` then `axiom skills apply`, `axiom skills list`.
- Pre-check: `python -m twine check dist/*`.

### C.4 MCP registry / server listing
- MCP spec baseline: https://modelcontextprotocol.io (2025-11-25 stable).
- Submit Axiom MCP server to https://github.com/modelcontextprotocol/servers (PR) and/or Smithery/Glama directories.
- Config already in `.mcp.json` (tracked generated file) — ensure `axiom_mcp/server.py` exposes 39 tools including skill tools.
- Docs: https://modelcontextprotocol.io/docs

### C.5 Marketplace submissions (user handles links)
| Marketplace | Submission path | Notes |
|---|---|---|
| skills.sh | Auto-index public GitHub repo | https://www.skills.sh |
| agentskill.sh | `npx @agentskill.sh/cli setup` + submit | https://agentskill.sh |
| agentskills.in | Submit via site | https://agentskills.in/marketplace |
| skills-hub.ai | Daily sync from GitHub sources | https://skills-hub.ai |
| AI Agents Directory | Submit form | https://aiagentsdirectory.com/skills |
| agentcatalog.ai | Security scan + certify | https://agentcatalog.ai |
| skillforagents.com | Submit | https://skillforagents.com |

### C.6 Awesome-list PRs (user handles)
Open PRs adding AxiomEmbedded to:
- https://github.com/VoltAgent/awesome-agent-skills
- https://github.com/kodustech/awesome-agent-skills
- https://github.com/seb1n/awesome-ai-agent-skills
- https://github.com/jqueryscript/awesome-agent-skills
- https://github.com/ningzimu/awesome-skills
- https://github.com/DevelopersGlobal/ai-agent-skills

### C.7 CI/CD for releases (recommended, user adds)
- `.github/workflows/release.yml`: on tag `v*` → build sdist/wheel → twine upload (OIDC trusted publishing) → create GitHub Release with notes.
- `.github/workflows/nightly-drift.yml`: already referenced in CONTRIBUTING; ensure it runs `skill_pipeline.py --check`, pytest, doctor.
- `.github/workflows/publish-skills.yml`: on push to main, notify skills.sh (no-op, auto-index).

### C.8 Documentation deliverables for global users
- README.md: what AxiomEmbedded is, install (`pip install axiom-cli`), quickstart (`axiom skills list`, `axiom skills apply`), skill count (237), license, contributing, links.
- docs/skills/AUTHORING_GUIDE.md (exists) — extend with Part A + B.
- CONTRIBUTING.md (exists) — merge gate already documented.
- SECURITY.md — vulnerability reporting (create).
- CODE_OF_CONDUCT.md (create, optional).

### C.9 Versioning & tagging
- Semver: current skills 1.2.0; ecosystem release target 1.3.0 (or 2.0.0 if breaking CLI changes).
- Tag format: `v1.3.0`.
- Keep `configs/project.yaml` version in sync.

### C.10 Post-release monitoring (user handles)
- Track GitHub stars/issues, skills.sh install counts, PyPI downloads.
- Autonomy KPI dashboard (backlog R10): human-intervention count, gate pass rate, eval success rate, token cost per artifact.
- Run nightly drift; respond to issues.

---

## Follow-ups not yet implemented (backlog)
- Eval harness `packages/eval/` (R7).
- Autonomy KPI dashboard (R10).
- `metadata.source` provenance field in manifest schema.
- Deprecation/superseded lifecycle state.
- `axiom skills discover` command (B.4).
- Rule files for hardware-aware checks.
- Profiles for embedded peripherals.
- EV-embedded-* evaluation tasks.
- Cloud/data/ML/web/mobile/observability domains.
- Run `skills-ref validate` on all skills.

## Identity / git
- Author: PRATIK082 <pratik.patil082@gmail.com>.
- Branches: `feat/embedded-skills-intelligence-initiative` (pushed), `feat/skill-ecosystem-strengthening` (local, `1f32f89`).
- No remote push performed by agent; user handles all pushes/releases above.
