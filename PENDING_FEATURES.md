# AxiomEmbedded -- Pending & Missing Features to Launch

Generated from a full audit of the repository (main @ e20987a, 2026-11-19).
Every item below is verified against the actual tree; no assumption-only claims.

## 0. Launch gate (must be green before tag v1.3.0)

- [x] `python -m compileall -q axiom_cli packages scripts` -- clean
- [x] `python -m pytest -q` -- 263 passed
- [x] `python -m axiom_cli doctor` -- PASS (repo PASS, tests SKIPPED ok)
- [x] `python -m axiom_cli repo validate` -- PASS
- [x] `python scripts/skill_pipeline.py --check` -- OK (275 skills)
- [x] `python scripts/audit_client_compat.py` -- 275/275
- [x] Version parity: pyproject / package.json / VERSION / configs/project.yaml all 0.2.0
- [ ] `python -m twine check dist/*` -- not yet run (user-handled publish)
- [ ] Tag `v1.3.0` push (user-handled)
- [ ] PyPI publish (user-handled)
- [ ] npm publish (user-handled)
- [ ] MCP registry PR (user-handled)

## 1. Documentation accuracy (DONE in this pass)

- [x] README skill counts updated (275 / 213 axiom-* / 62 legacy)
- [x] README MCP tool count updated (38)
- [x] BUILD_MANIFEST.json reconciled (275 skills, 30 agents, 0.2.0)
- [x] CHANGELOG.md entry added for 0.2.0 work
- [ ] docs/current-state-assessment.md still references 2026-10 state -- update or archive
- [ ] docs/AUDIT.md (2026-10-09) is stale -- mark superseded by this doc
- [ ] docs/ROADMAP.md Phases 0.3-1.0 still "planned" but many are done -- reconcile

## 2. Missing professional-repo files

- [ ] `CODE_OF_CONDUCT.md` (CONTRIBUTING references it; absent)
- [ ] `.github/workflows/release.yml` (tag -> build -> publish -> GitHub Release) -- referenced by global-release-plan C.5
- [ ] `.github/workflows/ci.yml` (PR gate: compileall + pytest + pipeline --check + doctor) -- currently split across 4 small workflows
- [ ] `SECURITY.md` contact/PGP details (file exists but minimal)
- [ ] Issue templates already present (bug_report, feature_request, skill_change) -- ok

## 3. Missing runtime / capability (from AUDIT.md, still open)

- [ ] `packages/eval/` eval harness -- referenced by global-release-plan follow-ups; absent
- [ ] Autonomy KPI dashboard -- referenced; absent
- [ ] Rule files for hardware-aware checks -- partial
- [ ] Profiles for embedded peripherals -- partial
- [ ] EV-embedded evaluation tasks -- only EV-001..EV-010 exist (agent-level); no skill-level evals
- [ ] Cloud/data/ML/web/mobile/observability domains -- partial coverage only
- [ ] Aerospace deepening -- only 1 aerospace skill (aerospace-defense-safety-review) is thin
- [ ] Cross-domain deepening -- only 1 (platform-architecture-review)
- [ ] `axiom doctor` OpenCode version re-verify (2.3.2 newer than surveyed 2.1.4) -- warning only

## 4. Skill content gaps (from master-production-plan sec.3)

- [ ] tests/: only 2 skills have non-empty tests/ with real content (exemplars); 273 skills have stub evals only
- [ ] scripts/: only ~13 skills have real validate.py; 262 are stubs
- [ ] references/: ~91 skills missing references
- [ ] templates/: ~144 skills missing templates
- [ ] contract fields: 64 legacy skills lack required_tools/inputs/outputs/artifact_types
- [ ] maturity: 69 production, 4 beta, 202 experimental -- most should be promoted as content deepens
- [ ] Description quality lint not enforced for legacy skills
- [ ] Progressive disclosure (body <= 500 lines) not enforced
- [ ] Safety gating: review_required not required for safety_critical skills

## 5. Framework gaps (from skill-ecosystem-gap-analysis sec.2)

- [ ] manifest.yaml not validated by validate_all (version drift possible)
- [ ] Runner does not propagate checker failures to status
- [ ] Disabled skills still engage (index/engage not filtering enabled)
- [ ] create_skill does not register catalog entry or facet parity
- [ ] Scaffold version mismatch (frontmatter 0.1.0 vs manifest 1.2.0) -- fixed for V&V skills only
- [ ] Enrichment only axiom-*; legacy skills never facet-checked
- [ ] Per-skill tests not run by pipeline
- [ ] No JSON schema validation of catalog.yaml
- [ ] No version compatibility check (catalog vs SKILL.md)
- [ ] No deprecation/superseded lifecycle
- [ ] No provenance/signing or versioned dependencies
- [ ] Runner is scaffold, not executor (no composition execution)
- [ ] No run-manifest schema validation
- [ ] Safety gating not enforced (review_required not required for safety_critical)

## 6. Agent/workflow/profile gaps

- [ ] agents.json omits 5 skill-* agents
- [ ] profiles.json omits skill-update-profile
- [ ] workflows.json omits embedded-skills-deep-update
- [ ] platforms.json count mismatch (26 vs 27 dirs)
- [ ] No agent for: skill evaluation, skill adoption, documentation generation, cloud/infra, data/ML
- [ ] No workflow for: skill adoption/import, evaluation runs, release of skill catalog

## 7. Rule gaps

- [ ] Missing rules: skill contract validation, description quality, progressive disclosure, eval requirement, provenance

## 8. Evaluation gaps

- [ ] Only EV-001..EV-010 (agent-level). No skill-level eval tasks.
- [ ] No EV-embedded-* tasks from prior initiative (deferred)

## 9. External adoption / discoverability

- [ ] MCP server registry submission (axiom_mcp/server.py, 38 tools) -- user-handled
- [ ] PyPI publish -- user-handled
- [ ] npm publish -- user-handled
- [ ] GitHub Release on tag -- needs release.yml workflow
- [ ] Badges in README (build, license, python version, skills count)
- [ ] Docs site (mkdocs.yml exists but not deployed)

## 10. Target audience for 50k+ users

Primary segments (verified from repo content + domains covered):

1. **Embedded firmware engineers** (C/C++/Rust on MCU/MPU) -- largest segment; skills: embedded-c, mcu, rtos, drivers, bootloader, build-system, debugging, static-analysis
2. **Automotive engineers** (AUTOSAR, ISO 26262, UDS, CAN) -- 32+ automotive skills
3. **Industrial/OT engineers** (IEC 61508, PLC, SCADA, Modbus) -- 37+ industrial skills
4. **Robotics engineers** (ROS2, motion control, safety) -- 52+ robotics skills
5. **Aerospace/defense engineers** (DO-178C, MIL-STD) -- growing
6. **IoT/edge AI engineers** (TinyML, edge inference, wireless) -- edge-ai, sensor-*, wireless-*
7. **Test/validation engineers** (HIL, SIL, MIL, Robot Framework) -- V&V framework (new)
8. **Safety/security engineers** (threat modeling, secure boot, fuzzing) -- safety-*, security-*, axiom-secure-*
9. **Students/educators** (learning embedded systems) -- examples/, docs/getting-started/
10. **AI/agent developers** (building engineering agents) -- agents/, skills framework, MCP

Channels to reach them: GitHub stars, PyPI downloads, MCP registry, embedded forums (EEVblog, Reddit r/embedded, r/FPGA), LinkedIn, YouTube tutorials, university partnerships, conference talks (Embedded World, ESC).

## 11. Professional-repo checklist (missing items)

- [ ] CODE_OF_CONDUCT.md
- [ ] SECURITY.md with real contact
- [ ] CONTRIBUTING.md merge gate (done)
- [ ] LICENSE (Apache-2.0, done)
- [ ] NOTICE (done)
- [ ] .github/workflows/ci.yml (unified)
- [ ] .github/workflows/release.yml
- [ ] mkdocs site deployed (GitHub Pages)
- [ ] Badges in README
- [ ] Examples verified working (7 examples exist)
- [ ] pipx install . tested end-to-end
- [ ] Docker image for reproducible environment

## 12. Immediate next actions (highest impact, lowest effort)

1. Add CODE_OF_CONDUCT.md + SECURITY.md contact
2. Add release.yml + ci.yml workflows
3. Add README badges
4. Update docs/current-state-assessment.md and docs/AUDIT.md (mark superseded)
5. Reconcile ROADMAP.md
6. Run twine check + npm pack verification
7. Submit MCP registry PR (user-handled, prep the .mcp.json)

These are the items I will start implementing now.
