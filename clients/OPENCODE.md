# AxiomEmbedded for OpenCode — install, use, and command reference

AxiomEmbedded is an open, AI-native engineering platform for embedded and
cyber-physical systems (Automotive, Aerospace, Defense, Industrial,
Robotics). This page covers **OpenCode only**: how to install the pack, what
it enables inside OpenCode, and every command/tool with usage and use cases.

> Cross-client matrix: `clients/MCP_CLIENTS.md`.
> Contributor view of the skill system: `docs/SKILL_FRAMEWORK.md`,
> `docs/skills/AUTHORING_GUIDE.md`, `docs/skills/GROUPS.md`.

## 1. What OpenCode gains

| Surface | What it is | How OpenCode sees it |
|---|---|---|
| Native skills | 93 `SKILL.md` packs under `.opencode/skills/` (58 base + 35 deep `axiom-*` automotive/embedded workflows) | Auto-discovered by OpenCode; invoke via `/axiom-*` commands or ask the agent |
| Agents | 29 specialist agents under `.opencode/agents/` (code-review, debugging, safety, …) | `opencode run --agent <name>` / TUI agent picker |
| Slash commands | 8 `/axiom-*` commands under `.opencode/commands/` | Type `/axiom-engage`, `/axiom-plan`, … in TUI/`run` |
| Policy plugin | `axiom-policy.ts` under `.opencode/plugins/` | Enforced guardrails (approvals, safety gates) |
| MCP server (37 tools) | `axiom mcp` over stdio, registered as `axiom-embedded` | Full CLI power callable by the model: engage, skills, plans, generators |
| `axiom oc` launcher | Runs OpenCode with an Axiom-isolated config | `axiom oc tui|run|research` — no pollution of your own config |

Skills are **data, not code**: adding one never needs a `.py` change. After
any skill edit a single command re-derives everything (`skills apply`).

## 2. Prerequisites

- Python **≥ 3.11**. Only runtime dependency: **PyYAML** (everything else is stdlib).
- OpenCode ≥ 1.18 (any recent release works; MCP shape is standard stdio).
- The repo checkout (or the pip package) — the installer copies content from it.

## 3. Install

### 3a. Get the `axiom` command

```bash
pipx install axiom-embedded        # recommended: `axiom` shim lands on PATH
# or
pip install axiom-embedded         # `python -m axiom_cli` fallback works too
# or from source
git clone https://github.com/PRATIK082/AxiomEmbedded
cd AxiomEmbedded
```

Check: `axiom version` → `0.2.0` (or `python -m axiom_cli version`).

### 3b. Install the pack into OpenCode

```bash
# Project scope (recommended): writes into the current project dir
axiom install --client opencode

# User-global: every OpenCode session on this machine
axiom install --client opencode --global

# Scoped copies: only the skills you need (faster context, less noise)
axiom install --client opencode --domains automotive
axiom install --client opencode --domains automotive,robotics --groups diagnostics,testing-verification

# Non-default target dir / content source / test home
axiom install --client opencode --path D:/work/ecu-proj --source D:/Project/GitHub/AxiomEmbedded
```

**What gets written (project scope):**

| Path | Content |
|---|---|
| `opencode.json` | Merges one key only: `mcp.axiom-embedded` → `{type: local, command: [axiom, mcp]}`. Existing keys untouched. |
| `.opencode/skills/*/SKILL.md` | The 93 skill packs (filtered by `--domains`/`--groups`; `domains=[all]` shared skills always included) |
| `.opencode/agents/*.md` | 29 specialist agents |
| `.opencode/commands/axiom-*.md` | 8 slash commands |
| `.opencode/plugins/axiom-policy.ts` | Policy plugin |

Global scope mirrors this under `~/.config/opencode/`. The installer
**merges, never clobbers**: files you edited that diverge from source are
kept and reported as `skipped`, never overwritten.

### 3c. Verify

```bash
axiom doctor                       # repo PASS + environment checks
opencode mcp list                  # `axiom-embedded` must appear
axiom skills list | head           # 93 catalog skills
axiom engage --domain automotive --platform mcu --limit 3   # scoped discovery works
```

In the TUI, type `/axiom-` — the 8 commands should autocomplete. Ask the
agent *"what axiom skills apply to CAN diagnostics?"* — it should reach for
`search_skills`/`engage` over MCP.

## 4. Using it day-to-day in OpenCode

### Slash commands (fastest path)

| Command | Runs | Use when |
|---|---|---|
| `/axiom-engage` | `engage --domain --platform` | Starting work: resolve which skills/profiles fit this project |
| `/axiom-plan` | `run` (plan-then-execute) | Turning a vague request into a phased, approval-gated plan |
| `/axiom-fix` | `fix <issue-id>` | 10-step defect plan for a known issue |
| `/axiom-feature` | `feature <feature-id>` | 9-step add-feature plan |
| `/axiom-research` | `research` | Deep question: planner → searchers → verifier → synthesizer |
| `/axiom-context` | `context select` | Pulling a bounded, relevant file set from the artifact graph |
| `/axiom-impact` | `impact` | Change blast-radius before editing |
| `/axiom-status` | `status` | Project health + recommended next action |

### Agents

`.opencode/agents/*.md` (29 files: `code-review`, `debugging`,
`root-cause`, `safety`, `security`, `test-engineering`, `hardware-bringup`,
`engineering-manager`, …). In TUI pick one for the session, or:

```bash
axiom oc run --agent debugging " Sporadic CAN frame loss at 500 kbit/s"
```

### The `axiom oc` launcher

Runs OpenCode with an **Axiom-isolated config** so trials never touch your
own `~/.config/opencode`:

```bash
axiom oc tui                                   # interactive TUI, isolated
axiom oc run "Review the UDS session handling" # single shot
axiom oc run --agent code-review --dir ./fw "Review drivers/can"
axiom oc run --no-isolate "..."                # use YOUR config instead
axiom oc run --dry-run "..."                   # print argv/env without executing
```

### MCP tools (37) — what the model can call

Discovery & skills:

| Tool | Purpose |
|---|---|
| `engage` | Skills + profiles for domain/platform/group (supports `limit`; reply carries `total`/`truncated`) |
| `search_skills` | Free-text search over the 93-skill catalog |
| `list_skills` / `read_skill` | Enumerate / load one `SKILL.md` |
| `skill_manifest` | Derived manifest.json for a skill (generated on demand; SKILL.md stays the source of truth) |
| `validate_skill` | Contract check for one skill (no writes) |
| `skill_pipeline` | One-command link/enrich/index/clients/validate; check-only unless `apply=true` |
| `link_skill` | Edit the skill graph in `catalog.yaml` (then pipeline) |
| `create_skill` | Scaffold a new `axiom-*` skill (dry-run unless `apply=true`) |
| `run_skill` | Execute a skill as a structured workflow (**dry-run default**; writes only under `output_dir`/`.axiom/runs`) |

Deterministic generators (all dry-run unless `output_path` is set; all paths repo-confined):

| Tool | Produces |
|---|---|
| `analyze_repository` | Artifact inventory (counts by type), read-only |
| `generate_checklist` | Skill gates merged to Markdown |
| `generate_test_plan` | Workflow steps → `VT-xx` verification rows |
| `generate_traceability_matrix` | Step × Inputs/Outputs/Evidence/Status CSV |
| `generate_report` | Run manifest or skill context → Markdown |
| `review_configuration` | YAML/JSON parse + secret scan (line numbers only, never values) |
| `analyze_trace` | CSV/TSV histograms + time-range, or log keyword counts |

Plans, analysis, system:

| Tool | Purpose |
|---|---|
| `run_plan` (`run`) | Plan-then-execute plan for a request |
| `route` | Route a request to the responsible specialist agent |
| `compose` | Skill mind-map DAG from a prompt + facet axes |
| `fix` / `feature` | 10-step defect / 9-step feature plans |
| `analyze` / `graph_build` / `context_select` / `impact` | Repo analysis, artifact graph, bounded context, blast radius |
| `research` | Deep-research pipeline (backends: auto/opencode/local/tavily/brave/searxng) |
| `packs` / `list_profiles` / `profile_validate` / `workflow_plan` | Tool-pack selection, profile listing/validation, lifecycle entry planning |
| `status` / `doctor` / `version` | Dashboard data, environment health, version |
| `install` / `uninstall` / `update` | Full pack lifecycle from inside the agent session (same semantics as CLI §3/§7) |

Safety rules the model follows: write-capable tools default to dry-run;
`approve`-gated actions (`git push`, release, destructive commands,
safety/security-critical changes) stop for human approval.

## 5. CLI command reference (all commands)

Every CLI command is also an MCP tool (§4) — same implementation
(`packages/axiom_sdk.py`), so both always agree.

```
axiom version | doctor [--skip-tests] | repo-validate
axiom install --client opencode [--global] [--path DIR] [--source DIR]
              [--domains d1,d2] [--groups g1,g2]
axiom uninstall --client opencode [--global] [--path DIR]
axiom update    --client opencode [--global] [--path DIR] [--source DIR]
              [--domains ...] [--groups ...]
axiom oc {tui|run|research} [--agent NAME] [--dir DIR] [--model M] [--no-isolate] [--dry-run]

axiom engage  --domain automotive --platform mcu [--group diagnostics] [--limit 5]
axiom run     "add watchdog supervision" --domain automotive --platform mcu
axiom route   "Sporadic CAN frame loss"
axiom fix     ISSUE-123 --domain automotive
axiom feature FEAT-45 --domain automotive
axiom research "AUTOSAR E2E vs CRC for ASIL-B" --backend local
axiom status [--format json]
axiom packs   --domain automotive --platform mcu --standard "ISO 14229-1"
axiom compose "Design UDS diagnostics for a gateway ECU" --domain automotive
axiom stage [PATH] [--profile P]        # lifecycle stage from evidence
axiom analyze [PATH] | graph build | context select --root <dir> | impact <project.yaml>
axiom workflow plan --profile P [--entry E]
axiom profile validate <path> | repo validate
axiom mcp                                # serve MCP over stdio
axiom serve --port 8765                  # REST + A2A over HTTP

axiom skills list
axiom skills search "uds" [--domain automotive]
axiom skills run axiom-diagnostics-uds --objective "..." [--target f.c] [--constraints ...] [--output DIR] [--apply]
axiom skills report axiom-diagnostics-uds .axiom/runs/<ts>/axiom-diagnostics-uds
axiom skills manifest axiom-diagnostics-uds
axiom skills create axiom-can-fd-timing --title "..." --domain automotive [--apply]
axiom skills link --set related_skills axiom-diagnostics-uds axiom-diagnostics-doip
axiom skills link --set extends        axiom-diagnostics-doip automotive-diagnostics
axiom skills validate                    # all skills + catalog + graph checks
axiom skills apply [--check]             # THE one command after any skill edit
```

Skill runs are **dry-run unless `--apply`** and write manifests to
`.axiom/runs/<timestamp>/<skill-id>/` (inputs, tools used, decisions, files,
warnings, acceptance checks).

## 6. Scoping: domains and groups

At 93 skills and growing, scope what the agent sees:

```bash
# Discovery-time scoping (no install needed)
axiom engage --domain automotive --platform mcu --limit 5
axiom engage --group diagnostics          # one of 16 views in skills/groups.yaml
axiom engage --domain automotive --group diagnostics --limit 5

# Install-time scoping (smaller .opencode/ copy)
axiom install --client opencode --domains automotive
axiom install --client opencode --groups diagnostics,testing-verification
```

Groups are **rule-based views** (`skills/groups.yaml`: `autosar-classic`,
`vehicle-networks`, `diagnostics`, `safety-security`, `adas`, `energy`,
`software-defined-vehicle`, `release-process`, `embedded-core`,
`testing-verification`, `robotics`, `industrial`, `aerospace-defense`,
`architecture`, `ways-of-working`, `autosar-adaptive`) — no directory moves,
every skill is guaranteed in ≥1 group, and the index carries a `by_group`
map. See `docs/skills/GROUPS.md`.

## 7. Update and uninstall

```bash
axiom update --client opencode            # re-install + report stale/force-refreshed files
axiom update --client opencode --global --domains automotive
axiom uninstall --client opencode         # unmerge MCP entry; delete copies only on byte-match
axiom uninstall --client opencode --global
```

Uninstall never touches your content: divergent (hand-edited) files are kept
and reported. Update lists `stale` files it kept so you can refresh each
explicitly.

## 8. End-to-end use cases

**A. New automotive ECU project (cold start).**
```bash
axiom install --client opencode --path ./gateway-ecu --domains automotive
cd gateway-ecu
axiom oc run "Engage automotive+mcu, then plan UDS diagnostics bring-up"
```
Agent calls `engage` → loads 2–3 `SKILL.md` context files → `run_plan` →
presents phased plan → you approve → `run_skill … --apply` writes reviewed
artifacts + run manifest.

**B. "What does this change break?" before a commit.**
Ask: *"axiom-impact of switching CAN driver to DMA"*. Agent calls `impact`
+ `trace_path`, returns blast radius; `/axiom-fix` drafts the defect plan if
a regression is found.

**C. Evidence pack for a release gate.**
```bash
axiom skills run axiom-automotive-release-readiness --objective "v2.3 gate" --apply
```
Produces checklist + traceability CSV + report under `.axiom/runs/…` —
attach to the release.

**D. Review a config without leaking secrets.**
Model calls `review_configuration(skill_id, config_path)` — parse results
plus secret findings as **line numbers only**.

**E. Grow the system (contribute a skill).**
```bash
axiom skills create axiom-can-fd-timing --title "CAN FD timing design" --domain automotive --apply
# ... write original SKILL.md + checklist + template ...
axiom skills link --set related axiom-can-fd-timing axiom-can-network-design
axiom skills apply          # enrich → index → clients → validate; mirrors regenerate
```
One command, no `.py` edits, CI (`skills apply --check` + pytest) proves it.
Full protocol: `docs/skills/AUTHORING_GUIDE.md`, `docs/skills/MULTI_AGENT_WORKFLOW.md`.

**F. Keep 10 sessions consistent.**
`axiom install --client opencode --global --groups diagnostics` once; every
project session inherits the same scoped pack + MCP server.

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| `opencode mcp list` lacks `axiom-embedded` | Re-run `axiom install --client opencode [--global]`; check `opencode.json` has `mcp.axiom-embedded` |
| `axiom: command not found` | `pipx install axiom-embedded`, or use `python -m axiom_cli …` everywhere (incl. MCP fallback in `clients/mcp.json`) |
| `/axiom-*` doesn't autocomplete | `.opencode/commands/` missing → re-install (project scope); global installs don't provide per-project commands |
| Agent sees all 93 skills (noisy) | Re-install with `--domains`/`--groups`, or start sessions with `engage --limit` |
| `skills apply` reports STALE/FAIL | Read the named step/file, fix the source (never hand-edit `registries/` or mirrors), re-run |
| `axiom doctor` fails | Run with `--skip-tests` to isolate env vs test failures; keep the 2 known pre-existing failures in mind (`dashboard_html`, research-citation test) |
