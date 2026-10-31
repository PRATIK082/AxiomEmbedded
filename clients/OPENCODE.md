# AxiomEmbedded for OpenCode -- install, use, and command reference

AxiomEmbedded is an open, AI-native engineering platform for embedded and
cyber-physical systems (Automotive, Aerospace, Defense, Industrial,
Robotics). This page covers **OpenCode only**: how to install the pack, what
it enables inside OpenCode, and every command/tool with usage and use cases.
Section 10 is the full taxonomy reference (domains, platforms, standards,
OS/languages/technologies, agents, skills) with cross-links.

> Cross-client matrix: `clients/MCP_CLIENTS.md`.
> Contributor view of the skill system: `docs/SKILL_FRAMEWORK.md`,
> `docs/skills/AUTHORING_GUIDE.md`, `docs/skills/GROUPS.md`.

## 1. What OpenCode gains

| Surface | What it is | How OpenCode sees it |
|---|---|---|
| Native skills | 93 `SKILL.md` packs under `.opencode/skills/` (58 base + 35 deep `axiom-*` automotive/embedded workflows) | Auto-discovered by OpenCode; invoke via `/axiom-*` commands or ask the agent |
| Agents | 29 specialist agents under `.opencode/agents/` (code-review, debugging, safety, ...) | `opencode run --agent <name>` / TUI agent picker |
| Slash commands | 8 `/axiom-*` commands under `.opencode/commands/` | Type `/axiom-engage`, `/axiom-plan`, ... in TUI/`run` |
| Policy plugin | `axiom-policy.ts` under `.opencode/plugins/` | Enforced guardrails (approvals, safety gates) |
| MCP server (37 tools) | `axiom mcp` over stdio, registered as `axiom-embedded` | Full CLI power callable by the model: engage, skills, plans, generators |
| `axiom oc` launcher | Runs OpenCode with an Axiom-isolated config | `axiom oc tui|run|research` -- no pollution of your own config |

Skills are **data, not code**: adding one never needs a `.py` change. After
any skill edit a single command re-derives everything (`skills apply`).

## 2. Prerequisites

- Python **>= 3.11**. Only runtime dependency: **PyYAML** (everything else is stdlib).
- OpenCode >= 1.18 (any recent release works; MCP shape is standard stdio).
- The repo checkout (or the pip package) -- the installer copies content from it
  (from a fresh clone the gitignored mirrors are generated on demand, so no
  manual `sync_clients.py` run is needed before installing).

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

Check: `axiom version` -> `0.2.0` (or `python -m axiom_cli version`).

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
| `opencode.json` | Merges one key only: `mcp.axiom-embedded` -> `{type: local, command: [axiom, mcp]}`. Existing keys untouched. |
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

In the TUI, type `/axiom-` -- the 8 commands should autocomplete. Ask the
agent *"what axiom skills apply to CAN diagnostics?"* -- it should reach for
`search_skills`/`engage` over MCP.

## 4. Using it day-to-day in OpenCode

### Slash commands (fastest path)

| Command | Runs | Use when |
|---|---|---|
| `/axiom-engage` | `engage --domain --platform` | Starting work: resolve which skills/profiles fit this project |
| `/axiom-plan` | `run` (plan-then-execute) | Turning a vague request into a phased, approval-gated plan |
| `/axiom-fix` | `fix <issue-id>` | 10-step defect plan for a known issue |
| `/axiom-feature` | `feature <feature-id>` | 9-step add-feature plan |
| `/axiom-research` | `research` | Deep question: planner -> searchers -> verifier -> synthesizer |
| `/axiom-context` | `context select` | Pulling a bounded, relevant file set from the artifact graph |
| `/axiom-impact` | `impact` | Change blast-radius before editing |
| `/axiom-status` | `status` | Project health + recommended next action |

### Agents

`.opencode/agents/*.md` (29 files: `code-review`, `debugging`,
`root-cause`, `safety`, `security`, `test-engineering`, `hardware-bringup`,
`engineering-manager`, ...). In TUI pick one for the session, or:

```bash
axiom oc run --agent debugging " Sporadic CAN frame loss at 500 kbit/s"
```

#### Enabling an agent (no extra step)

Installing already enables everything: `axiom install --client opencode`
writes one `.md` per agent, and OpenCode **auto-discovers** any `*.md` under
`.opencode/agents/` (project scope) or `~/.config/opencode/agents/` (global
scope). There is no registry to update, no flag to flip -- if the file is
there, the agent exists. Verify with:

```bash
ls .opencode/agents/              # 29 files after install
```

Each file carries OpenCode-native frontmatter (auto-derived from
`agents/*/manifest.json` -- never hand-edit the copies):

```yaml
name: code-review
description: Reviews source changes against architecture, rules, tests and scope.
mode: subagent
permission:
  edit: deny        # read-only agents can't modify files; implementers say `allow`
  bash:
    '*': ask        # every shell command needs your approval
    git push *: deny
```

#### Activation paths (4 ways)

| # | Path | How | Example |
|---|---|---|---|
| 1 | TUI picker | Open the agent switcher in `opencode` TUI, choose e.g. `safety` | interactive session runs under that agent's contract |
| 2 | `axiom oc run --agent` | Launcher passes `--agent <name>` straight through to `opencode run` | `axiom oc run --agent code-review --dir ./fw "Review drivers/can"` |
| 3 | Ask the model | Any OpenCode session: *"use the debugging agent..."* -- the `description` field is what the model matches on, so name + description are the activation keywords | *"Have the root-cause agent build hypotheses for the reset fault"* |
| 4 | MCP `route` (any client) | `route("Sporadic CAN frame loss")` -> returns `debugging`; the model then loads that agent's contract | works identically in Claude, Cursor, OpenCode -- no agent files needed client-side |

#### How an agent works at runtime

An agent file is an **operating contract**, not a script. When active, the
model must: (1) use the artifact graph before broad reads, (2) load only the
profile + workflow + rules + evidence relevant to the task (typically via
`engage` -> `context_files`), (3) emit structured findings with evidence
references, (4) stay inside declared scope. Capability and safety rails come
from `agents/<name>/manifest.json`: `capabilities`, `permissions`
(`filesystem: read`, `git_push: false`), and `approval.required_for`
(push, release, destructive, safety/security-critical). OpenCode enforces the
`permission:` frontmatter itself; the MCP/CLI side enforces the same policy
via `APPROVAL_REQUIRED_FOR` in `axiom_sdk` -- so TUI, `oc run`, and MCP agree.

#### Other CLI tools

| Tool | Agent support |
|---|---|
| Claude Code | Same file-copy model: install writes `.claude/agents/*.md`; native `/agents` handling |
| Codex | No agent files -- reads root `AGENTS.md`; route via `axiom route` / MCP `route` |
| Cursor / Cline / Aider / Kilo / OpenHands / Gemini / Copilot | No local agent files (runtime via MCP): model calls `route` -> `read_skill` -> `run_skill`; identical behavior, zero copies to keep fresh |

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

### MCP tools (37) -- what the model can call

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
| `generate_test_plan` | Workflow steps -> `VT-xx` verification rows |
| `generate_traceability_matrix` | Step x Inputs/Outputs/Evidence/Status CSV |
| `generate_report` | Run manifest or skill context -> Markdown |
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
| `install` / `uninstall` / `update` | Full pack lifecycle from inside the agent session (same semantics as CLI S3/S7) |

Safety rules the model follows: write-capable tools default to dry-run;
`approve`-gated actions (`git push`, release, destructive commands,
safety/security-critical changes) stop for human approval.

## 5. CLI command reference (all commands)

Every CLI command is also an MCP tool (S4) -- same implementation
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
`architecture`, `ways-of-working`, `autosar-adaptive`) -- no directory moves,
every skill is guaranteed in >=1 group, and the index carries a `by_group`
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
Agent calls `engage` -> loads 2-3 `SKILL.md` context files -> `run_plan` ->
presents phased plan -> you approve -> `run_skill ... --apply` writes reviewed
artifacts + run manifest.

**B. "What does this change break?" before a commit.**
Ask: *"axiom-impact of switching CAN driver to DMA"*. Agent calls `impact`
+ `trace_path`, returns blast radius; `/axiom-fix` drafts the defect plan if
a regression is found.

**C. Evidence pack for a release gate.**
```bash
axiom skills run axiom-automotive-release-readiness --objective "v2.3 gate" --apply
```
Produces checklist + traceability CSV + report under `.axiom/runs/...` --
attach to the release.

**D. Review a config without leaking secrets.**
Model calls `review_configuration(skill_id, config_path)` -- parse results
plus secret findings as **line numbers only**.

**E. Grow the system (contribute a skill).**
```bash
axiom skills create axiom-can-fd-timing --title "CAN FD timing design" --domain automotive --apply
# ... write original SKILL.md + checklist + template ...
axiom skills link --set related axiom-can-fd-timing axiom-can-network-design
axiom skills apply          # enrich -> index -> clients -> validate; mirrors regenerate
```
One command, no `.py` edits, CI (`skills apply --check` + pytest) proves it.
Full protocol: `docs/skills/AUTHORING_GUIDE.md`, `docs/skills/MULTI_AGENT_WORKFLOW.md`.

**F. Keep 10 sessions consistent.**
`axiom install --client opencode --global --groups diagnostics` once; every
project session inherits the same scoped pack + MCP server.

## 10. Taxonomy reference (domains . platforms . standards . OS . technologies . agents . skills)

Everything below is generated from, or points at, repo source -- not prose.
Counts match the `0.2.0` tree (93 skills, 29 agents, 16 groups).

### 10.1 Domains

Two levels: repo-wide domain overlays in [`../domains/`](../domains/) (policies,
profiles, reference content) and the per-skill `domain` facet in
[`../skills/catalog.yaml`](../skills/catalog.yaml) that drives discovery.

Repo domain overlays (15):

| Overlay | Focus |
|---|---|
| `automotive` | AUTOSAR Classic/Adaptive, CAN/Ethernet, UDS/DoIP, functional safety, cybersecurity, ADAS, BMS, V2X, zonal/SDV |
| `aerospace` | DO-178C/DO-254-style safety evidence workflows |
| `defense` | Rugged/mission-critical embedded, secure boot concepts |
| `industrial` | PLC-adjacent control review, fieldbus, IEC 61508 awareness |
| `robotics` | ROS 2, sensor fusion, motion control, autonomy interfaces |
| `energy` | BMS-adjacent/energy systems (see `energy` group) |
| `generic-embedded` | Bare-metal/RTOS firmware, drivers, bring-up -- reusable anywhere |
| `consumer`, `iot`, `marine`, `medical`, `rail`, `semiconductor`, `space`, `telecom` | Overlay stubs: profile + manifest ready, skill coverage grows on demand |

Skill-catalog `domain` values (what `engage --domain` and `--domains` match):

| Value | Skills | Meaning |
|---|---|---|
| `all` | 41 | Cross-cutting: copied for ANY `--domains` filter, always in discovery |
| `automotive` | 32 | Automotive-only workflows (AUTOSAR, networks, diagnostics, ADAS, BMS, ...) |
| `generic-embedded` | 9 | Portable firmware/testing/bring-up skills |
| `platform` | 6 | Architecture/platform-review skills |
| `robotics` | 2 | ROS 2 / system-integration skills |
| `aerospace` | 1 | Aerospace/defense safety review |
| `industrial` | 1 | Industrial control review |
| `cross-domain` | 1 | Shared engineering workflow |

```bash
axiom engage --domain automotive --platform mcu --limit 5   # 76 total, paged
axiom install --client opencode --domains automotive,robotics
```

### 10.2 Platforms

Platform overlays in [`../platforms/`](../platforms/) (27): compute
`arm-cortex-m/a/r`, `risc-v`, `tricore`, `rh850`, `powerpc`, `x86`, `xtensa`,
`dsp`, `gpu`, `npu`, `fpga`, `mcu`, `mpu`, `soc`, `mpsoc`; OS/RTOS
`bare-metal`, `freertos`, `zephyr`, `nuttx`, `embedded-linux`, `rtos`,
`ros2`; standards `autosar-classic`, `autosar-adaptive`; plus `generic`.

Skill-level `platforms` bindings (what `--platform` and `by_platform` match --
a skill lists every target it applies to, so counts overlap):

| Platform | Skills | Typical use |
|---|---|---|
| `mcu` | 46 | 8/16/32-bit microcontroller firmware |
| `mpu` | 44 | Microprocessor / application-core software |
| `all` | 32 | Platform-agnostic process skills |
| `soc` / `mpsoc` | 18 / 9 | Heterogeneous SoC, domain/zonal controllers |
| `autosar-classic` | 14 | OSEK/OIL, BSW, RTE, COM stack work |
| `autosar-adaptive` | 11 | ara::com, execution/state management |
| `bare-metal` | 7 | No-OS firmware, bootloaders, drivers |
| `rtos` | 7 | FreeRTOS/Zephyr-style tasking reviews |
| `linux` | 4 | Embedded-Linux userspace, gateway/SDV compute |

```bash
axiom engage --domain automotive --platform autosar-classic
```

### 10.3 Standards (17, as declared by skills)

Guidance references, never certification claims -- safety/security outputs
always carry a human-review gate.

| Area | Standards |
|---|---|
| Functional safety | `ISO 26262:2018`, `IEC 61508` |
| Cybersecurity | `ISO/SAE 21434` |
| Coding | `MISRA C`, `CERT C` |
| Aerospace | `DO-178C`, `DO-254` |
| In-vehicle comms & diagnostics | `AUTOSAR Classic R24-11`, `AUTOSAR Adaptive R24-11`, `AUTOSAR` (general), `AUTOSAR SOME/IP`, `ISO 11898` (CAN), `ISO 13400-2` (DoIP), `ISO 14229-1` (UDS), `IEEE 802.1 TSN`, `ETSI ITS-G5` (V2X) |
| Process | `Automotive SPICE` |

Matching rule (`packs`/`compose`): tools with an empty `standards` facet are
generic and always match; otherwise at least one requested standard must be
listed. Pass through literally, e.g.:

```bash
axiom packs --domain automotive --platform mcu --standard "ISO 14229-1"
axiom compose "Design UDS diagnostics for a gateway ECU" --domain automotive --standard "ISO 14229-1"
```

### 10.4 OS, languages, hardware, technologies

`os` and `languages` are **profile-driven enums** (see [`../profiles/`](../profiles/),
e.g. [`../profiles/automotive-mcu.yaml`](../profiles/automotive-mcu.yaml)):

| Axis | Values | Where it binds |
|---|---|---|
| `os` | `autosar-classic`, `bare-metal`, `embedded-linux`, `generic`, `linux`, `ros2`, `rtos` | `profiles/*.yaml` -> `stage`, `run_plan`, agent context |
| `languages` | `c`, `cpp`, `python`, `rust` | profiles -> review/analysis scope |
| `hardware` | free-form (`arm-cortex-m`, `tricore`, `soc`, ...) | `compose --hardware`; carried in output schema for future index scoring |
| `technology` | free-form (`mcu`, `soc`, `soc-class-gateway`, ...) | `compose --technology`; same passthrough |
| `lifecycle` | profile value (`v-model`, ...) + skill `lifecycle` facet | `stage` detects phase from evidence |

### 10.5 Agents (29)

Contracts live in [`../agents/`](../agents/) (`AGENT.md` + `manifest.json`
per agent); OpenCode copies go to `.opencode/agents/*.md`. Purpose quotes
are verbatim from each manifest.

| Agent | Purpose |
|---|---|
| `ai-validation` | Evaluates embedded AI models for accuracy, resource use and deployment readiness. |
| `brownfield-recovery` | Recovers architecture, dependencies, tests and baselines from an existing product. |
| `change-impact` | Computes change impact across the artifact graph. |
| `code-review` | Reviews source changes against architecture, rules, tests and scope. |
| `debugging` | Reproduces faults and drives root-cause analysis. |
| `dependency-analysis` | Builds module, symbol and dependency relationships. |
| `diag-auto-review` | Binds an external CLI review/fix agent to Axiom diag skills. |
| `documentation` | Generates and updates engineering documentation from artifacts. |
| `engineering-manager` | Plans multi-step engineering work, gates and evidence. |
| `hardware-architecture` | Models compute, memory, peripherals, boards and HW/SW boundaries. |
| `hardware-bringup` | Guides hardware/software bring-up and evidence capture. |
| `implementation` | Implements scoped code changes under project rules. |
| `intent-router` | Routes a user request to the smallest engineering workflow and context slice. |
| `migration` | Plans legacy/standard/platform migrations with rollback evidence. |
| `performance` | Analyses CPU, memory, timing, power and latency constraints. |
| `project-audit` | Audits repository health, traceability and process completeness. |
| `release` | Assembles release evidence and release metadata. |
| `requirements` | Creates, normalizes, decomposes and traces requirements. |
| `root-cause` | Builds evidence-backed causal hypotheses and verification plans. |
| `safety` | Performs safety-oriented evidence and gate checks without claiming certification. |
| `security` | Performs secure-development and threat-oriented checks. |
| `skill-implementer` / `skill-orchestrator` | Task agents (writes enabled): implement / orchestrate skill work. |
| `skill-researcher` / `skill-verifier` | Task agents (read-only): research / verify skill work. |
| `software-architecture` | Designs software components, interfaces, concurrency and deployment. |
| `static-analysis` | Aggregates and explains static-analysis findings. |
| `system-architecture` | Maintains system architecture models and interfaces. |
| `test-engineering` | Designs and executes unit, integration, regression and system testing. |

Use in OpenCode: TUI agent picker, or `axiom oc run --agent debugging "..."`,
or MCP `route` to let the model choose. Permissions/approvals per agent are
in its `manifest.json` (`git_push: false`, approval gates, ...).

### 10.6 Skills by group (93, 16 rule-based views)

Groups are defined in [`../skills/groups.yaml`](../skills/groups.yaml) as
OR-of-AND match rules over id/domain/subdomain/tags/maturity -- **views, not
folders** (a skill may appear in two groups). Full metadata per skill:
[`../skills/catalog.yaml`](../skills/catalog.yaml); full text:
[`../skills/`](../skills/). Maturity:  production .  beta .  experimental.
`axiom engage --group <id>` / `axiom install --client opencode --groups <ids>`.

**autosar-classic** (6): [autosar](../skills/autosar/SKILL.md)  .
[axiom-autosar-classic-architecture](../skills/axiom-autosar-classic-architecture/SKILL.md)  .
[axiom-autosar-classic-bsw-integration](../skills/axiom-autosar-classic-bsw-integration/SKILL.md)  .
[axiom-autosar-com-stack](../skills/axiom-autosar-com-stack/SKILL.md)  .
[axiom-autosar-os-config](../skills/axiom-autosar-os-config/SKILL.md)  .
[axiom-autosar-rte-design](../skills/axiom-autosar-rte-design/SKILL.md) 

**autosar-adaptive** (2): [automotive-middleware](../skills/automotive-middleware/SKILL.md)  .
[axiom-autosar-adaptive-deployment](../skills/axiom-autosar-adaptive-deployment/SKILL.md) 

**vehicle-networks** (4): [automotive-networks](../skills/automotive-networks/SKILL.md)  .
[axiom-automotive-ethernet-someip](../skills/axiom-automotive-ethernet-someip/SKILL.md)  .
[axiom-can-network-design](../skills/axiom-can-network-design/SKILL.md)  .
[axiom-can-stack-integration](../skills/axiom-can-stack-integration/SKILL.md) 

**diagnostics** (3): [automotive-diagnostics](../skills/automotive-diagnostics/SKILL.md)  .
[axiom-diagnostics-doip](../skills/axiom-diagnostics-doip/SKILL.md)  .
[axiom-diagnostics-uds](../skills/axiom-diagnostics-uds/SKILL.md) 

**safety-security** (6): [automotive-cybersecurity](../skills/automotive-cybersecurity/SKILL.md)  .
[axiom-aerospace-defense-safety-review](../skills/axiom-aerospace-defense-safety-review/SKILL.md)  .
[axiom-functional-safety](../skills/axiom-functional-safety/SKILL.md)  .
[axiom-vehicle-cybersecurity](../skills/axiom-vehicle-cybersecurity/SKILL.md)  .
[safety](../skills/safety/SKILL.md)  . [security](../skills/security/SKILL.md) 

**adas** (3): [adas](../skills/adas/SKILL.md)  .
[axiom-adas-perception-pipeline](../skills/axiom-adas-perception-pipeline/SKILL.md)  .
[axiom-adas-validation](../skills/axiom-adas-validation/SKILL.md) 

**energy** (2): [axiom-bms-design](../skills/axiom-bms-design/SKILL.md)  .
[axiom-bms-diagnostics](../skills/axiom-bms-diagnostics/SKILL.md) 

**software-defined-vehicle** (5): [automotive-body](../skills/automotive-body/SKILL.md)  .
[automotive-cockpit](../skills/automotive-cockpit/SKILL.md)  .
[automotive-ota](../skills/automotive-ota/SKILL.md)  .
[axiom-v2x-communication](../skills/axiom-v2x-communication/SKILL.md)  .
[axiom-zonal-architecture](../skills/axiom-zonal-architecture/SKILL.md) 

**release-process** (15): [automotive-coding](../skills/automotive-coding/SKILL.md)  .
[automotive-spice](../skills/automotive-spice/SKILL.md)  .
[automotive-vcycle](../skills/automotive-vcycle/SKILL.md)  .
[axiom-automotive-release-readiness](../skills/axiom-automotive-release-readiness/SKILL.md)  .
[change-impact](../skills/change-impact/SKILL.md)  .
[configuration-management](../skills/configuration-management/SKILL.md)  .
[documentation](../skills/documentation/SKILL.md)  . [evidence](../skills/evidence/SKILL.md)  .
[legacy-recovery](../skills/legacy-recovery/SKILL.md)  .
[project-audit](../skills/project-audit/SKILL.md)  . [release](../skills/release/SKILL.md)  .
[requirements](../skills/requirements/SKILL.md)  .
[requirements-traceability](../skills/requirements-traceability/SKILL.md)  .
[traceability](../skills/traceability/SKILL.md)  . [validation](../skills/validation/SKILL.md) 

**embedded-core** (25): [ai-validation](../skills/ai-validation/SKILL.md)  .
[axiom-embedded-firmware-bringup](../skills/axiom-embedded-firmware-bringup/SKILL.md)  .
[axiom-hil-test-planning](../skills/axiom-hil-test-planning/SKILL.md)  .
[axiom-memory-and-performance-analysis](../skills/axiom-memory-and-performance-analysis/SKILL.md)  .
[axiom-rtos-architecture](../skills/axiom-rtos-architecture/SKILL.md)  .
[axiom-test-automation](../skills/axiom-test-automation/SKILL.md)  .
[axiom-trace-analysis](../skills/axiom-trace-analysis/SKILL.md)  .
[bare-metal](../skills/bare-metal/SKILL.md)  . [bootloader](../skills/bootloader/SKILL.md)  .
[debugging](../skills/debugging/SKILL.md)  . [drivers](../skills/drivers/SKILL.md)  .
[edge-ai](../skills/edge-ai/SKILL.md)  . [embedded-c](../skills/embedded-c/SKILL.md)  .
[embedded-cpp](../skills/embedded-cpp/SKILL.md)  .
[embedded-linux](../skills/embedded-linux/SKILL.md)  .
[fault-injection](../skills/fault-injection/SKILL.md)  .
[hardware-architecture](../skills/hardware-architecture/SKILL.md)  .
[hardware-bringup](../skills/hardware-bringup/SKILL.md)  . [mcu](../skills/mcu/SKILL.md)  .
[mpsoc](../skills/mpsoc/SKILL.md)  . [mpu](../skills/mpu/SKILL.md)  .
[performance](../skills/performance/SKILL.md)  . [rtos](../skills/rtos/SKILL.md)  .
[rust-embedded](../skills/rust-embedded/SKILL.md)  . [soc](../skills/soc/SKILL.md) 

**testing-verification** (9): [axiom-hil-test-planning](../skills/axiom-hil-test-planning/SKILL.md)  .
[axiom-static-analysis-triage](../skills/axiom-static-analysis-triage/SKILL.md)  .
[axiom-test-automation](../skills/axiom-test-automation/SKILL.md)  .
[coverage](../skills/coverage/SKILL.md)  .
[integration-test](../skills/integration-test/SKILL.md)  .
[simulation](../skills/simulation/SKILL.md)  . [system-test](../skills/system-test/SKILL.md)  .
[test-automation](../skills/test-automation/SKILL.md)  . [unit-test](../skills/unit-test/SKILL.md) 

**robotics** (2): [axiom-robotics-system-integration](../skills/axiom-robotics-system-integration/SKILL.md)  .
[robotics](../skills/robotics/SKILL.md) 

**industrial** (1): [axiom-industrial-control-review](../skills/axiom-industrial-control-review/SKILL.md) 

**aerospace-defense** (1): [axiom-aerospace-defense-safety-review](../skills/axiom-aerospace-defense-safety-review/SKILL.md) 

**architecture** (5): [architecture](../skills/architecture/SKILL.md)  .
[axiom-architecture-decision-records](../skills/axiom-architecture-decision-records/SKILL.md)  .
[axiom-interface-contract-design](../skills/axiom-interface-contract-design/SKILL.md)  .
[axiom-platform-architecture-review](../skills/axiom-platform-architecture-review/SKILL.md)  .
[software-architecture](../skills/software-architecture/SKILL.md) 

**ways-of-working** (7): [axiom-embedded-cicd](../skills/axiom-embedded-cicd/SKILL.md)  .
[axiom-technical-debt-assessment](../skills/axiom-technical-debt-assessment/SKILL.md)  .
[build-system](../skills/build-system/SKILL.md)  . [code-review](../skills/code-review/SKILL.md)  .
[feature-development](../skills/feature-development/SKILL.md)  .
[implementation](../skills/implementation/SKILL.md)  .
[static-analysis](../skills/static-analysis/SKILL.md) 

Skill-to-skill links (`related_skills` / `extends` / `sub_skills` /
domain & platform overlays) live in the same
[`catalog.yaml`](../skills/catalog.yaml) -- single source, edited via
`axiom skills link --set`, enforced by `axiom skills validate`. Adding a
group = one rule block in [`groups.yaml`](../skills/groups.yaml), no folder
moves. Rule semantics: [`../docs/skills/GROUPS.md`](../docs/skills/GROUPS.md).

### 10.7 How the facets connect (cross-link map)

```
request --engage(domain, platform, group, limit)--> skills + profiles + context_files
                |                       |
   domains/ overlays          platforms/ overlays
   profiles/*.yaml --os/languages/lifecycle--> stage . run_plan . agent context
   skills/catalog.yaml --domain/subdomain/tags/maturity--> groups.yaml views --> by_group index
   skills/*/SKILL.md --platforms/standards/inputs/outputs--> run_skill . generators
   standards requested --packs--> tool/pip packs (empty facet = generic = always matches)
   agents/*/manifest.json --capabilities/permissions/approval--> route . oc --agent . MCP
```

Entry points per role: OpenCode user -> S4-S6 of this doc; skill author ->
[`../docs/skills/AUTHORING_GUIDE.md`](../docs/skills/AUTHORING_GUIDE.md);
parallel-agent teams ->
[`../docs/skills/MULTI_AGENT_WORKFLOW.md`](../docs/skills/MULTI_AGENT_WORKFLOW.md);
framework standard -> [`../docs/SKILL_FRAMEWORK.md`](../docs/SKILL_FRAMEWORK.md).

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| `opencode mcp list` lacks `axiom-embedded` | Re-run `axiom install --client opencode [--global]`; check `opencode.json` has `mcp.axiom-embedded` |
| `axiom: command not found` | `pipx install axiom-embedded`, or use `python -m axiom_cli ...` everywhere (incl. MCP fallback in `clients/mcp.json`) |
| `/axiom-*` doesn't autocomplete | `.opencode/commands/` missing -> re-install (project scope); global installs don't provide per-project commands |
| Agent sees all 93 skills (noisy) | Re-install with `--domains`/`--groups`, or start sessions with `engage --limit` |
| `skills apply` reports STALE/FAIL | Read the named step/file, fix the source (never hand-edit `registries/` or mirrors), re-run |
| `axiom doctor` fails | Run with `--skip-tests` to isolate env vs test failures; keep the 2 known pre-existing failures in mind (`dashboard_html`, research-citation test) |
