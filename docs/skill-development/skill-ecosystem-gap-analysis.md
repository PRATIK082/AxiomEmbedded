# Skill Ecosystem Gap Analysis — All Skills (Phase 2)

**Date:** 2026-11-09
**Branch:** feat/embedded-skills-intelligence-initiative (extended)
**Scope:** All 200 skills across all domains, plus framework, registries, agents, workflows, profiles, rules, evaluation.

## 1. Baseline inventory
- 200 skills: 138 `axiom-*` (127 experimental, 7 production, 4 beta) + 62 legacy (production).
- Domains: automotive 32, robotics 52, industrial 37, all 47, generic-embedded 16, platform 14, aerospace 1, cross-domain 1.
- Structure: SKILL.md + manifest.yaml (all); checklists 195/200; references 161/200; scripts 28/200; templates 108/200.
- 30 agents, 10 workflows, 10 profiles, 13 rules, 15 domains, 27 platforms, 43 standards, 9 technologies.
- Registries drift: agents.json omits 5 skill-* agents; profiles.json omits skill-update-profile; workflows.json omits embedded-skills-deep-update; platforms.json 26 vs 27 dirs.

## 2. Framework gaps (from inspection)
1. manifest.yaml not validated by `validate_all` (version drift possible).
2. Runner does not propagate checker failures to status.
3. Disabled skills still engage (index/engage not filtering enabled).
4. `create_skill` does not register catalog entry or facet parity.
5. Scaffold version mismatch (frontmatter 0.1.0 vs manifest 1.2.0).
6. Enrichment only `axiom-*`; legacy skills never facet-checked.
7. Per-skill tests not run by pipeline.
8. No JSON schema validation of catalog.yaml.
9. No version compatibility check (catalog vs SKILL.md).
10. No deprecation/superseded lifecycle.
11. No provenance/signing or versioned dependencies.
12. Runner is scaffold, not executor (no composition execution).
13. No run-manifest schema validation.
14. Safety gating not enforced (review_required not required for safety_critical).

## 3. Skill content gaps (research-derived)
- **Contract fields:** inputs/outputs/required_tools/optional_tools/mcp_tools/risk_level/review_required/safety_critical/lifecycle/related_skills/artifact_types not uniformly present; not enforced for beta/production.
- **Description quality:** vague/first-person/trigger-poor descriptions likely across legacy skills; no lint.
- **Progressive disclosure:** no body-length lint; no reference-depth lint.
- **Gates:** checklists free-form; no machine-executable gate schema; only 28 skills have scripts.
- **Eval:** no per-skill eval harness; evaluation/ only has 5 EV tasks.
- **Safety:** builder/reviewer pairs exist for industrial/robotics assurance skills but not uniformly; no impact-assessment gate enforcement.
- **Naming:** legacy skills use short names (adas, rtos) vs axiom- prefix convention; mixed.
- **Sub-skill grouping:** groups.yaml covers 18 groups but many skills may be orphaned? Invariant enforces coverage; need verify.
- **Provenance:** no `metadata.source` for adopted skills.
- **Autonomy KPI:** no metrics dashboard.

## 4. External adoption gaps (high-value skills not yet in catalog)
Meta/agent-engineering:
- skill-creator (with eval loop + description optimization)
- mcp-builder
- tool-schema-design
- agent-evaluation, agent-observability, human-in-the-loop, multi-agent-orchestration
- prompt-injection-defense, agent-red-teaming
- awesome-skills-purge (catalog hygiene)
- clean-ai-slop, improve-codebase-architecture, diagnosing-bugs, karpathy-guidelines
- awesome-git-commit-plan, awesome-code-explainer, awesome-agents-md-generator
- cto-advisor, awesome-api-design
- context-engineering (prompt budget optimization)

Security/testing:
- security-best-practices, security-threat-model, security-ownership-map
- mcp-security-testing (confused deputy, SSRF, token passthrough, tool-output injection)

Documentation/media:
- doc-coauthoring, pdf/docx/xlsx/pptx document skills
- frontend-design

Conversion/provenance:
- Skill_Seekers-style doc→SKILL.md conversion
- metadata.source upstream link

## 5. Domain coverage gaps
- Aerospace: only 1 skill (aerospace-defense-safety-review) — thin.
- Cross-domain: 1 (platform-architecture-review) — thin.
- Generic-embedded: 16 — moderate; could add storage/memory/timers (done for embedded), but more: power-management, OTA, logging/tracing, boot-time optimization.
- All-domain core: 47 — broad but many are legacy generic; could strengthen with modern equivalents.
- Missing domains: cloud/infra, data/ML, web/frontend, mobile, testing (dedicated), documentation, project management, observability, compliance automation.

## 6. Agent/workflow/profile gaps
- agents.json omits 5 skill-* agents.
- profiles.json omits skill-update-profile.
- workflows.json omits embedded-skills-deep-update.
- platforms.json count mismatch (26 vs 27).
- No agent for: skill evaluation, skill adoption, documentation generation, cloud/infra, data/ML.
- No workflow for: skill adoption/import, evaluation runs, release of skill catalog.

## 7. Rule gaps
- 13 rules; missing: skill contract validation rule, skill description quality rule, progressive disclosure rule, eval requirement rule, provenance rule.

## 8. Evaluation gaps
- Only EV-001..EV-005 (agent-level). No skill-level eval tasks. No EV-embedded-* from prior initiative (deferred).

## 9. Priority matrix
P0 (framework hardening, CI): items 1-14 framework gaps, description lint, progressive disclosure lint, safety gating, manifest validation, runner propagation, enabled filtering, catalog registration, version parity, schema validation.
P1 (adoption): meta-skills (skill-creator, mcp-builder, debugging-methodology, etc.), security skills, documentation skills.
P2 (enhancement): backfill contract fields, checklists yaml gates, scripts scaffold, eval harness, metrics dashboard, provenance field, deprecation lifecycle.
P3 (coverage): new domains (cloud, data/ML, web, testing, observability), aerospace/cross-domain deepening, EV-embedded-* tasks, agent/workflow/profile additions.

## 10. Success criteria
- `skill_pipeline.py --check` green; pytest green; doctor green.
- Every skill has valid manifest + contract fields (for beta/production).
- Every skill matches >=1 group (already).
- Description quality lint passes for all skills.
- Progressive disclosure lint passes (body <=500 lines, refs one level).
- At least 3 eval scenarios per production skill.
- Safety-critical skills have review_required + impact assessment gate.
- Autonomy KPI tracked (human-intervention count per run).
- New meta-skills adopted and validated.
PY