# ADR-0004: Skill packaging for multi-harness use

- Status: accepted
- Date: 2026-10-03
- Scope: all 47 skills, v1.1.0 -> v1.2.0

## Context

Skills were content-complete but undiscoverable outside this repo: no
`SKILL.md` frontmatter (Claude Code / OpenCode / Codex / Antigravity all
require `name` + `description`), no declared domain/platform linkage, and no
way to engage a project-relevant slice or run axiom standalone.

## Decision

1. One facet source of truth: `registries/skill-facets.yaml`
   (description with use-triggers, domains, platforms; `all` wildcard).
2. Generated `registries/skill-index.json` with reverse indexes
   (`by_domain`, `by_platform`).
3. `scripts/add_frontmatter.py` injects frontmatter and bumps manifests to
   v1.2.0 (content unchanged, packaging-only).
4. `packages/skills/engage.py` + `axiom engage` resolve domain/platform
   slices and suggest profiles; `axiom run` emits opencode-like
   plan-then-execute plans with the host harness supplying the model.
5. `scripts/install_skills.py` copies skill folders (full or sliced) into any
   harness skills directory.

## Consequences

- Skills work unmodified in four harnesses via the shared agent-skills format.
- Engagement is deterministic and auditable (same filters -> same skill set).
- `axiom run` does not execute model calls itself; execution stays in the
  host harness behind existing approval gates.
