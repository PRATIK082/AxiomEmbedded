# Multi-agent skill workflow

How multiple AI agents (or humans + AI) work on skills in parallel without
stepping on each other — and without anyone memorizing update procedures.

## The one rule

> **Edit DATA, then run ONE command. Never hand-edit GENERATED files.**

```bash
python -m axiom_cli skills apply          # link -> enrich -> index -> clients -> validate
python -m axiom_cli skills apply --check  # verify only (what CI runs)
```

The same pipeline is one MCP call: `skill_pipeline` (`apply=true` to write,
default is check-only). Tell the AI exactly this sentence:

> "When you finish changing any skill, run `skill_pipeline` with apply=true.
> If it reports error, fix what it names and re-run. Do not hand-edit
> registries/, client mirrors, or catalog facets."

That single instruction replaces the old 5-script procedure. Forgetting a
step is now impossible: there is only one step.

## Data vs generated (ownership map)

| Layer | Files | Who edits | Parallel rule |
|---|---|---|---|
| L0 skill content | `skills/<id>/SKILL.md`, `templates/`, `checklists/`, `scripts/`, `examples/` | Any agent | **One skill dir per agent.** Never two agents in the same dir. |
| L1 relationships | `skills/catalog.yaml` graph keys (related/extends/sub_skills/overlays) | Agent owning the new skill | Edit only your skill's entry via `skills link --set`; never touch others' entries. |
| L2 catalog facets | `skills/catalog.yaml` facet fields | Nobody by hand | `enrich` backfills from SKILL.md frontmatter. If a facet is wrong, fix the frontmatter, not the catalog. |
| L3 generated | `registries/*.json`, `.opencode/skills/*`, `.claude/skills/*`, `GEMINI.md`, `copilot-instructions.md` | Nobody by hand | Pipeline regenerates. CI fails on drift (`--check`). |
| L4 framework code | `packages/*`, `axiom_mcp/*`, `axiom_cli/*`, `scripts/*` | Senior agent/human only | Adding a skill NEVER needs this. Only new *tool kinds* do. |

## Parallel-work protocol

1. **Claim a skill directory** (one agent = one `skills/<id>/` dir, or one
   domain subtree like `skills/automotive/*`). Your catalog graph entries are
   yours to edit via `skills link --set`.
2. **Scaffold, don't copy**: `axiom skills create <id> --title ... --apply`
   (or MCP `create_skill` with apply=true), then write original content.
3. **Finish with the pipeline**: run `skills apply` (CLI) or `skill_pipeline`
   apply=true (MCP). Green = mergeable. Red = the report names the exact
   file/field — fix and re-run.
4. **Merge gate**: a branch merges only when `skills apply --check`,
   `pytest`, and `doctor` are green. The pipeline is idempotent: re-running
   on a clean tree changes zero files, so concurrent agents can't corrupt
   each other through it.
5. **Conflicts**: two agents editing different catalog entries merge cleanly
   (one YAML mapping per skill). If both touch one entry or one SKILL.md,
   that violates rule 1; reassign.

## Using skills for feature development (any domain)

Skills are consumers of the same pipeline, not just its product:

- `run_skill` (CLI `skills run`, MCP) executes a skill as a structured
  workflow with dry-run default — safe for an AI to propose, human to apply.
- Generator tools (`generate_checklist`, `generate_test_plan`,
  `generate_traceability_matrix`, `generate_report`, `review_configuration`,
  `analyze_trace`, `analyze_repository`) turn skill content into reviewable
  artifacts during feature work.
- `engage(domain, platform)` + `install --domains` scope an agent session
  to one domain: `axiom install --client opencode --domains automotive`
  copies only matching skills (plus `domains=[all]` shared skills); MCP
  discovery filters the same way at runtime.

## Why no .py edits as skills grow

- New skill → data files only. Discovery (catalog, index, mirrors, agent
  configs) is derived by the pipeline.
- New domain/platform binding → frontmatter lists + pipeline. The install
  `--domains` filter reads the generated index, so it follows automatically.
- New tool kind → one function in `packages/skill_tools.py` + one TOOLS
  entry + tests. This is the only case that touches framework code, and it
  is deliberately rare (7 generators cover all 35 axiom-* skills today).
