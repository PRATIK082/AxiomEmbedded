# Domain-aware agent execution (Tab-select + auto skill binding)

Every specialist agent (`agents/*/AGENT.md`, Tab-selectable in OpenCode / Claude /
Codex) keeps a **fixed identity** but adapts its **skill slice and checklists**
to the current project. A `code-review` stays a `code-review`; on an
automotive project it reviews as automotive (MISRA + ISO 26262 + ASPICE), on a
defense project as defense (DO-178C-informed + IEC 61508 + hardening).

## How it works (runtime, every run — Step 0)

Each agent executes **Step 0 — Resolve project context** before any analysis:

1. **Explicit file (wins):** `./axiom.project.yaml` or `./.axiom/project.yaml`
   (copy from `axiom.project.yaml.example`). Schema:
   `schemas/axiom-project.schema.json`.
2. **Repo signals:** `packages/agents/project_context.py` scans file names +
   `README.md` / `AGENTS.md` for `repo_signals` in
   `configs/domain-routing.yaml` (e.g. `arxml/dbc` → automotive,
   `do-178/arinc` → aerospace, `plc/modbus` → industrial).
3. **Prompt keywords:** `packages/agents/router.py::detect_domain()` (all
   domains; canonical lists in `configs/domain-routing.yaml`).
4. **Fallback:** `generic-embedded` + `generic-embedded` profile.

Then the agent calls `axiom engage --domain X --platform Y` (i.e.
`packages/skills/engage.py`) and loads, in order (project AND prompt union):

- **Core skill** — same-name skill (`code-review` → `code-review` skill; full
  map in `configs/domain-routing.yaml::agent_binding.core_skill_by_agent`).
- **Domain priority skills** — e.g. automotive adds
  `axiom-functional-safety`, `axiom-vehicle-cybersecurity`,
  `axiom-diagnostics-uds`; defense adds the **shared**
  `axiom-aerospace-defense-safety-review` + `safety`/`security`.
- **Platform + group skills** from the domain's `skill_groups`
  (see `skills/groups.yaml` views).
- **Standards checklists** as metadata identifiers only (never normative
  text, never a compliance claim).

The full cross-map is generated:
`registries/agent-domain-matrix.json` (via
`scripts/generate_agent_domain_matrix.py`) — agent × domain → skills,
platforms, standards, profiles.

## Runtime clarification (no silent guessing)

`resolve_project_context()` returns `confidence`, `needs_clarification`, and a
ready-to-ask `clarification_question`. The agent MUST ask and wait when:
nothing was detected (fallback, confidence 0.2), repo and prompt disagree
(conflict, ~0.55), or confidence is below `runtime.ask_threshold` (0.5). Ask
via the host question tool (OpenCode question, Claude AskUserQuestion, or chat
prompt) with the candidate domains; re-resolve only after the user picks.

## Token efficiency (production rule)

`load_plan = {core, primary[], deferred[]}`. Open at most `primary_cap`
SKILL.md files (default 8) before analysis; keep `context_files` within
`max_context_files` (default 8). Consult `deferred` only on demand — never
bulk-load the matrix.

## Production-grade output (deployment-ready verdict)

Every run ends with a machine-checkable verdict block: `verdict, domain_used,
skills_loaded, skills_deferred, standards_applied, evidence_refs,
approval_gate, followups` (see `runtime.production_output_contract`).
`approval_gate` names the required human approval per `configs/project.yaml`;
the agent never auto-approves.

## How a user links a new development (future-proofing)

Scenario: you add a new subsystem, domain variant, or standard.

1. **Declare the project:** create/update `axiom.project.yaml` in the target
   repo (`domain/platform/os/profile/standards`). Commit it — agents pick it
   up with zero code changes.
2. **Add/extend the skill:** scaffold with
   `axiom skills create <id> --title ... --domain <domain>`, implement
   `SKILL.md`, then `python scripts/skill_pipeline.py` (link→enrich→index→
   clients→validate) to rebuild `registries/skill-index.json`.
3. **Link the cross-map (single sources only):**
   - Domain vocabulary/facets: `registries/skill-facets.yaml` (+
     `taxonomies/domains.yaml` if a brand-new domain).
   - Group view: `skills/groups.yaml` (rule-based, no file moves).
   - Domain routing: `configs/domain-routing.yaml` — add keywords,
     `repo_signals`, `platforms`, `standards`, `skill_groups`,
     `priority_skills`, `default_profile`.
   - Graph links: `axiom skills link --set related_skills|extends|...`
     (edits `skills/catalog.yaml`, the single source).
4. **Regenerate derived artifacts (never hand-edit):**
   `python scripts/generate_agent_domain_matrix.py`,
   `python scripts/sync_clients.py` (refreshes `.opencode/agents/*.md`,
   `.claude/agents/*.md`, `opencode.json`, mirrors),
   `python -m pytest -q tests/test_domain_routing.py tests/test_detect.py`.
5. **Verify the agent sees it:**
   `axiom engage --domain <new> --platform <p>` lists the skill;
   `axiom run "<request>"` shows `domain_source` + skill slice.

## Fixed gaps (this change)

- `detect_domain()` knew **automotive only** → now all domains
  (automotive/defense/aerospace/industrial/robotics/energy/iot/
  generic-embedded), sourced from `configs/domain-routing.yaml`.
- No explicit project file → `axiom.project.yaml(.example)` + schema added.
- Agents had no Step 0 → all `agents/*/AGENT.md` now carry the
  domain-aware preamble; manifests declare `domain_aware: true` +
  `requires_project_context: true`.
- Defense/aerospace thin slices documented: defense reuses the shared
  `axiom-aerospace-defense-safety-review` (no duplicate skill by design);
  remaining depth comes from `safety`/`security`/`fault-injection`/platform
  core skills — see matrix `notes`.
