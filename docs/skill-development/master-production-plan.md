# AxiomEmbedded Master Production Plan (E2E)

**Owner:** AI agent (full ownership granted). **Branch:** `feat/skill-ecosystem-strengthening`. **Remote:** https://github.com/PRATIK082/AxiomEmbedded.git. **License:** Apache-2.0. **No reference traces in shipped skills** (provenance kept only in internal register).

## 0. Mission
Make AxiomEmbedded globally visible and every skill production-grade, independent, self-contained, and machine-verifiable. Use all available skills from study (embedded + agent-engineering + cloud/edge/quality). Execute in batches; inform user only on decisions.

## 1. Production-grade skill criteria (must hold for maturity >= beta)
Each skill directory contains and passes:
- `SKILL.md` — spec-compliant frontmatter (name/description/version/domains/platforms) + `axiom:` contract block (inputs, outputs, required_tools, optional_tools, mcp_tools, risk_level, review_required, safety_critical, lifecycle, related_skills, artifact_types, maturity, owner, tags, standards).
- `manifest.yaml` — version parity with SKILL.md.
- `checklists/review.yaml` — >= 1 machine-readable gate.
- `tests/` — >= 3 eval scenarios (`evals.json`) for production; >= 1 for beta.
- `scripts/` — `validate.py` (stdlib, deterministic, errors explicit).
- `references/` — >= 1 reference doc (one level deep).
- `templates/` — >= 1 template where artifact-producing.
- Description: third-person, 40-1024 chars, states what + when, no vague terms.
- SKILL.md body <= 500 lines; references one level deep.
- ASCII-clean; no mojibake; forward-slash paths.
- `enabled` respected by engage + sync.
- Passes `skills-ref validate` (agentskills spec) for portability.
- CI gate green: pipeline --check, pytest, doctor, repo validate, compileall.

## 2. Independence (decoupling)
- Skills must not depend on repo-internal paths beyond declared inputs.
- Each skill's `scripts/validate.py` runs standalone with stdlib only.
- `required_tools` declared; no assumed packages.
- Dry-run by default for any write-capable operation.
- No cross-skill file imports; composition via `related_skills` + artifact types.
- Domain overlays loaded only when project context matches.

## 3. Gap audit (current state, 237 skills)
- tests/: 1 skill has non-empty tests/ (axiom-autosar-classic-bsw-integration) → need 236.
- scripts/: 13 skills → need 224.
- checklists/: 232 ok, 5 missing.
- references/: 146 ok, 91 missing.
- templates/: 93 ok, 144 missing.
- contract fields: 64 legacy skills lack `required_tools` (and some lack inputs/outputs/artifact_types).
- maturity: 69 production, 4 beta, 164 experimental.

## 4. Missing skills to add (suitable for product/agents)
Mapped from study (Jeffallan 67, SkillClaw evolution, deer-flow harness, opencode docs, codex-skills, awesome lists) filtered to embedded/edge/cloud/quality/agent-engineering fit. New `axiom-*` skills (experimental initially):

### Cloud/Edge/Infra (for connected embedded products)
- axiom-cloud-architecture (AWS/Azure/GCP for edge fleets)
- axiom-kubernetes-edge (K8s for edge gateways/fleet orchestration)
- axiom-terraform-infra (IaC for test farms/cloud infra)
- axiom-monitoring-observability (logging/metrics/tracing for devices)
- axiom-sre-reliability (SLO/SLA, incident response for fleets)
- axiom-chaos-engineering (resilience/fault injection at system level)
- axiom-cli-developer (CLI design for axiom_cli itself + device CLIs)

### Data/ML (edge AI)
- axiom-prompt-engineering (LLM prompt design for on-device/edge agents)
- axiom-rag-architect (RAG for technical docs/knowledge bases)
- axiom-data-pipeline (telemetry ETL, time-series)
- axiom-database-optimization (telemetry storage, Postgres/Timescale)

### API/Integration
- axiom-api-design (REST/contract design — already have interface-contract-design; add OpenAPI-focused)
- axiom-graphql-architect
- axiom-microservices-architect (service-oriented ECUs / edge services)
- axiom-websocket-engineer (real-time device comms)
- axiom-mcp-developer (MCP server dev — we have mcp-builder meta; add engineering-focused)

### Quality/Review
- axiom-test-master (unified test strategy)
- axiom-playwright-e2e (HIL/web test automation)
- axiom-code-reviewer (deep review skill)
- axiom-code-documenter (inline/API docs)
- axiom-debugging-wizard (systematic root-cause)
- axiom-legacy-modernizer (brownfield recovery deep)

### Security
- axiom-secure-code-guardian
- axiom-security-reviewer

### Agent/Meta (already added 27 in Phase F1; verify coverage)
- skill-creator, mcp-builder, tool-schema-design, agent-evaluation, agent-observability, human-in-the-loop, multi-agent-orchestration, prompt-injection-defense, agent-red-teaming, skills-purge, diagnosing-bugs, improve-codebase-architecture, clean-ai-slop, git-commit-plan, code-explainer, agents-md-generator, api-design, cto-advisor, security-best-practices, security-threat-model, security-ownership-map, mcp-security-testing, doc-coauthoring, document-skills, frontend-design, context-engineering, skill-seekers.

### SkillClaw-inspired (self-evolving skills) — optional, user decision
- axiom-skill-evolution (dedup/improve/verify skills from session data) — meta. Recommend adding as experimental.

Total new: ~30. Decision point: confirm scope (cloud/edge vs core embedded). Default: add all as experimental, refine later.

## 5. Execution batches (agent-driven)

### Batch 0 — Audit + baseline (done)
- Audit script results recorded above.

### Batch 1 — Production criteria enforcement in code
- `packages/skills/validator.py`: require contract fields for beta/production (R1); manifest.yaml validation + version parity (already added F0); progressive disclosure lint <=500 lines + refs one level; description quality lint.
- `packages/skills/loader.py`: description quality lint (F0 done), safety gating.
- `packages/skills/runner.py`: checker failures propagate (F0 done), plan-validate-execute mode, safety gate.
- `packages/skills/engage.py`: filter disabled (F0 done).
- Add `scripts/check_production_grade.py` linter: tests/, scripts/validate.py, references/, checklists, contract fields, desc length.

### Batch 2 — Automated scaffolding (all 237 skills)
- For each skill missing tests/: create `tests/evals.json` with 3 stub scenarios derived from description + acceptance.
- For each missing scripts/: create `scripts/validate.py` from template, customized with skill id.
- For each missing references/: create `references/overview.md` stub with standards placeholders.
- For each missing templates/: create `templates/artifact.template.md` stub.
- For each missing checklists/: create from template.
- Backfill contract fields (required_tools/inputs/outputs/artifact_types) for legacy skills using sensible defaults per domain.

### Batch 3 — New missing skills (~30)
- Scaffold via create_skill.py (auto catalog + facet parity).
- Mark experimental; minimal but complete structure.

### Batch 4 — Content refinement (top 20 production skills)
- Deepen content for production skills and the 10 new high-value ones.

### Batch 5 — Groups + registries
- Update groups.yaml with new groups (cloud-edge, data-ml, api-integration, quality-review, security-guard).
- Regenerate registries via pipeline apply.
- Agent-domain-matrix regenerate.

### Batch 6 — Tests + CI
- Update test counts.
- Add tests/test_production_grade.py.
- Add .github/workflows/release.yml, nightly-drift.yml.

### Batch 7 — Global visibility
- README, CHANGELOG, SECURITY.md, badges.
- Push branch, PR, tag (user approval for merge/push to main).

### Batch 8 — Verification
- Full gate + skills-ref validate + secret scan.

## 6. Decision points for user
D1: Scope of new skills (all ~30 vs core-only). Default: all experimental.
D2: SkillClaw-style self-evolving skills (yes/no). Default: add axiom-skill-evolution as experimental.
D3: Push to origin feature branch now? (permission granted by "keep push to git branch" → yes, feature branch only).
D4: Merge to main / tag release → requires explicit approval (AGENTS.md).

## 7. Execution log
(Updated as batches complete.)
- Batch 0: done (audit).
- Next: Batch 1.

## 8. Files touched (running)
- docs/skill-development/global-release-plan.md (prior)
- docs/skill-development/master-production-plan.md (this)
- (to be updated)
