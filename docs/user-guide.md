# AxiomEmbedded User Guide

Welcome to AxiomEmbedded v1.3.1 — an AI-native engineering platform for embedded
and cyber-physical systems. This guide covers **installation, every command
with examples, the dashboard UI, all five interfaces, and using the skills in
your own projects**.

## Contents

1. [Install](#1-install)
2. [Quickstart (60 seconds)](#2-quickstart-60-seconds)
3. [CLI reference with examples](#3-cli-reference-with-examples)
4. [Dashboard UI](#4-dashboard-ui)
5. [Using AxiomEmbedded in your own project](#5-using-axiomembedded-in-your-own-project)
6. [Interfaces: REST, MCP, A2A, Python SDK](#6-interfaces-rest-mcp-a2a-python-sdk)
7. [AI-client setup (Claude, opencode, Copilot, Cursor, …)](#7-ai-client-setup)
8. [Interface × client matrix](#8-interface--client-matrix)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Install

**Prerequisites:** Python 3.11 or newer. No other dependencies — the runtime
uses the standard library only (`PyYAML` + `pytest` are the only declared
packages).

```powershell
# 1. Clone
git clone <your-fork-url> AxiomEmbedded
cd AxiomEmbedded

# 2. (Recommended) create a virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install editable with test extras
pip install -e ".[test]"

# 4. Verify the install
python -m axiom_cli doctor
python -m axiom_cli repo validate
```

Expected output of `doctor`:

```text
AxiomEmbedded doctor
- python: 3.14.3        # your version may differ (>= 3.11 is fine)
- repo: PASS
- tests: PASS
```

`repo validate` prints `Repository validation: PASS`.

> **Linux/macOS:** replace `py -3.11` with `python3.11` and use
> `source .venv/bin/activate`. Everything else is identical.
> Windows users who hit a `cp1252` console-encoding error should run
> `chcp 65001` first (UTF-8 mode).

---

## 2. Quickstart (60 seconds)

```powershell
# Project health at a glance
python -m axiom_cli status

# Pick the skills for YOUR domain + platform (example: car + microcontroller)
python -m axiom_cli engage --domain automotive --platform mcu

# Turn a task into an execution plan
python -m axiom_cli run "add watchdog driver" --domain automotive --platform mcu

# Open the web dashboard (then visit http://127.0.0.1:8765)
python -m axiom_cli serve
```

That's the whole loop: **status → engage → run → verify**.

---

## 3. CLI reference with examples

The binary is `axiom` (installed as a console script) or
`python -m axiom_cli`. All examples below use `axiom` for brevity — substitute
`python -m axiom_cli` if the script isn't on your `PATH`.

### 3.1 `axiom status` — terminal dashboard

```powershell
axiom status
axiom status --format json
```

What it prints (real output, abbreviated):

```text
AXIOMEMBEDDED - AxiomEmbedded [HEALTHY]
Skills: 47 at v1.2.0  ####################
  schemas      19
  profiles     9
  workflows    10
  agents       28
  domains      15
  tests        6

NEEDS ATTENTION
  None — all systems nominal.

RECOMMENDED: axiom run 'next feature'
```

- `[HEALTHY]` / `[ATTENTION]` tells you whether anything needs action.
- The bar chart is ASCII on purpose (Windows-safe).
- `--format json` emits the same data for scripts/CI:
  `skills`, `inventory`, `needs_attention[]`, `recommended_next_action`.

### 3.2 `axiom engage` — select skills for your domain + platform

```powershell
# Full slice for a car project on a microcontroller
axiom engage --domain automotive --platform mcu

# Other projects
axiom engage --domain robotics --platform soc
axiom engage --domain aerospace --platform mpu
axiom engage --domain industrial              # no platform filter
axiom engage --platform linux                 # no domain filter
axiom engage                                  # everything (all 47 skills)
```

Real output for `--domain robotics --platform soc` (abbreviated):

```json
{
  "domain": "robotics",
  "platform": "soc",
  "skill_count": 37,
  "profiles": ["skill-update-profile"],
  "skills": ["ai-validation", "architecture", "bootloader", "...", "robotics", "soc", "..."],
  "context_files": ["skills/robotics/SKILL.md", "skills/soc/SKILL.md", "..."]
}
```

How to use it:

- `skills[]` — the exact skill folder names relevant to your project.
- `profiles[]` — matching overlay profiles (e.g. `automotive-mcu` when one
  exists for your combo, plus the generic `skill-update-profile`).
- `context_files[]` — the `SKILL.md` paths to load into your AI assistant.
  Paste these into Claude/opencode/Copilot (see §7), or let
  `install_skills.py` copy them for you (see §5.2).

Valid `--domain` values: `generic-embedded automotive aerospace defense iot
industrial robotics`. Valid `--platform` values include `mcu mpu soc mpsoc
linux rtos bare-metal arm riscv` (see `registries/skill-facets.yaml` for the
full vocabulary).

### 3.3 `axiom run` — turn a request into an execution plan

```powershell
axiom run "add watchdog driver" --domain automotive --platform mcu
axiom run "migrate bootloader to A/B updates" --domain industrial --platform mcu
axiom run "tune motion planner latency" --domain robotics --platform soc
```

What it returns (structure, lists abbreviated):

```json
{
  "mode": "plan-then-execute",
  "request": "add watchdog driver",
  "intent": "engineering-manager",
  "engagement": { "domain": "automotive", "platform": "mcu",
                  "skill_count": 42, "profiles": ["automotive-mcu", "skill-update-profile"],
                  "skills": ["mcu", "drivers", "safety", "..."] },
  "phases": ["plan", "implement", "verify", "evidence"],
  "approval_required_for": ["git push", "release", "destructive_command",
                            "safety_critical_change", "security_critical_change"]
}
```

The model executing the phases is **your AI assistant** (Claude, opencode,
Copilot…): paste the plan output into it together with the `context_files`
from `engage`, and it works the phases. Anything in `approval_required_for`
stops for a human — the plan never auto-pushes, auto-releases, or
auto-applies safety/security-critical changes.

### 3.4 `axiom fix` / `axiom feature` — ready-made plan emitters

```powershell
axiom fix BOOT-123 --domain automotive --platform mcu
axiom feature OTA-DELTA --domain industrial --platform mcu
```

Output is a JSON plan envelope:

```json
{
  "mode": "plan-then-execute",
  "kind": "fix",
  "issue_id": "BOOT-123",
  "steps": ["intent", "context", "impact", "root_cause", "patch",
            "tests", "analysis", "review", "evidence", "pr"],
  "engagement": { "domain": "automotive", "platform": "mcu", "skill_count": 42, "...": "..." },
  "evidence_target": "docs/compliance/evidence/",
  "approval_required_for": ["git push", "release", "destructive_command",
                            "safety_critical_change", "security_critical_change"]
}
```

`feature` emits the same envelope with `"kind": "feature"` and a 9-step list.
Feed the JSON to your assistant; it executes step by step and drops evidence
under `docs/compliance/evidence/`.

### 3.5 `axiom serve` — REST + A2A server and dashboard

```powershell
axiom serve                 # http://127.0.0.1:8765
axiom serve --port 8931     # custom port
```

Keep it running in a terminal; open the URL in a browser for the dashboard
(see §4). The same server answers the REST and A2A APIs (see §6). Stop with
`Ctrl+C`. The server binds to `127.0.0.1` (local only) by design.

### 3.6 `axiom mcp` — Model Context Protocol server over stdio

```powershell
axiom mcp
```

Speaks newline-delimited JSON-RPC 2.0 on stdin/stdout. You don't type into it —
your MCP client (Claude Code, opencode, Cursor, …) spawns it. Exposed tools:

| Tool | Purpose |
|------|---------|
| `engage` | Same slice as CLI `engage` (`domain`, `platform` args) |
| `run_plan` | Same plan as CLI `run` (`request`, `domain`, `platform`) |
| `get_status` | Same data as CLI `status` |
| `plan_fix` / `plan_feature` | Same envelopes as CLI `fix` / `feature` |
| `read_skill` | Full `SKILL.md` body for one skill id |
| `list_skills` / `list_profiles` | Inventory discovery |

Minimal client config (`clients/mcp.json` exists in-repo as a portable template —
no hardcoded paths; run from the project root or install the `axiom` entry point):

```json
{
  "mcpServers": {
    "axiom": { "command": "axiom", "args": ["mcp"] }
  }
}
```

Fallback when `axiom` is not on `PATH`:

```json
{
  "mcpServers": {
    "axiom": { "command": "python", "args": ["-m", "axiom_cli", "mcp"] }
  }
}
```

OpenCode uses a different shape (`command` is an argv array, `type: "local"`).
`axiom install --client opencode` and `scripts/sync_clients.py` already emit it:

```json
{ "mcp": { "axiom": { "type": "local", "command": ["axiom", "mcp"],
                       "enabled": true } } }
```

### 3.7 Built-in platform commands (pre-existing)

These ship with the repo and are unrelated to the feature work, but listed
here so the reference is complete:

| Command | Example | Purpose |
|---------|---------|---------|
| `doctor` | `axiom doctor` | Environment + repo self-check |
| `repo validate` | `axiom repo validate` | Validate registries/manifests |
| `profile` | `axiom profile --help` | Profile inspection |
| `analyze` / `graph` / `context` / `impact` | `axiom impact --help` | Artifact-graph queries |
| `workflow` / `route` | `axiom route "add driver"` | Route a request to a workflow |
| `research` | `axiom research "question" --backend local` | Deep-research pipeline (see §3.8) |

Run any of them with `--help` for flags.

### 3.8 Deep research (`axiom research`)

Planner → searchers → verifier → synthesizer. `question` is split into up
to `--max-subquestions` (default 3) focused sub-questions; each runs against
the selected `--backend`, findings are deduped and uncited claims are
rejected (listed honestly under Rejected), and the markdown report always
ends with the safety notice. Standards text is paraphrase-only: findings
carry number/version/clause/source, never normative prose.

| Backend | Needs | Behaviour |
|---|---|---|
| `auto` (default) | opencode binary if present | OpenCode `skill-researcher` subagent per sub-question; falls back to `local` per question when the binary is unusable |
| `opencode` | opencode binary (+ model credentials for live runs) | As above, no silent fallback except to `local` on unavailable |
| `local` | nothing (always available, CI-safe) | Keyword search over `skills/*/` manifests + SKILL.md headings |
| `tavily` / `brave` / `searxng` | `TAVILY_API_KEY` / `BRAVE_API_KEY` / `SEARXNG_URL` | Honestly `unavailable` without credentials (live web search out of scope for this change); falls back to `local` |

```bash
axiom research "ISO 26262 automotive safety" --backend local
axiom research "question" --format markdown --output report.md
```

The same pipeline is the `research` MCP tool (`question`, `backend`,
`max_subquestions`, `model`).

---

## 4. Dashboard UI

Start it with `axiom serve` and open `http://127.0.0.1:8765`. It is a single
stdlib-generated HTML page (no JavaScript, no build step) with three cards:

```text
+----------------------------------------------------------+
| AxiomEmbedded                                        [h1] |
+----------------------------------------------------------+
| PROJECT HEALTH: AxiomEmbedded — HEALTHY            [card] |
|   Skills: 47 (latest v1.2.0)                             |
|   +-----------------------+                              |
|   | schemas      | 19     |  <- inventory table            |
|   | profiles     | 9      |                              |
|   | workflows    | 10     |                              |
|   | agents       | 28     |                              |
|   | domains      | 15     |                              |
|   | tests        | 6      |                              |
|   +-----------------------+                              |
+----------------------------------------------------------+
| NEEDS ATTENTION                                    [card] |
|   * None — all systems nominal.                          |
|     (or: [HIGH] <id>: <title>                            |
|      <suggested axiom command>)                           |
+----------------------------------------------------------+
| RECOMMENDED NEXT ACTION                            [card] |
|   axiom run 'next feature'                               |
+----------------------------------------------------------+
```

- **Card 1** mirrors `axiom status`: state, skill versions, inventory counts.
- **Card 2** lists attention items (each with severity and the exact command
  to run) or "all systems nominal".
- **Card 3** shows the single recommended command — copy-paste it into a
  terminal.
- Refresh the page to update (no auto-refresh by design — slice 2 candidate).

---

## 5. Using AxiomEmbedded in your own project

Pick the path that matches how much you want to adopt.

### Path A — Copy skills into your AI assistant (simplest)

```powershell
# Install ALL skills for opencode (also: claude, codex, antigravity)
python scripts/install_skills.py --harness opencode --dest C:\YourProject\.opencode\skills

# ...or only the slice your project needs (example: drone on SoC + Linux)
python scripts/install_skills.py --harness claude --dest C:\DroneProject\.claude\skills \
    --domain robotics --platform soc
```

Each installed skill is a folder with `SKILL.md` (now frontmatter-headed, so
every harness auto-discovers it). Re-run after `git pull` to pick up updates.

### Path B — Reference skills without copying (zero duplication)

1. Run `axiom engage --domain <yours> --platform <yours>` and keep the
   `context_files[]` list.
2. Paste those `SKILL.md` paths (or their contents) into your assistant's
   context alongside your task. The assistant follows the skill's rules,
   gates, and evidence conventions in your repo.
3. For plans, paste the output of `axiom run` / `axiom fix` / `axiom feature`.

### Path C — Drive it from your own code (SDK / REST)

```python
import sys
sys.path.insert(0, "C:/D/Project/GitHub/AxiomEmbedded/packages")
from axiom_sdk import engage_skills, run_plan, get_status

slice = engage_skills(domain="automotive", platform="mcu")  # 42 skills
plan = run_plan("add watchdog driver", domain="automotive", platform="mcu")
health = get_status()  # same data as `axiom status --format json`
```

Or over HTTP while `axiom serve` runs (curl examples in §6.1).

### Which skills does MY project need? (worked examples)

| Your project | Command | You get |
|--------------|---------|---------|
| Car ECU on Cortex-M + FreeRTOS | `engage --domain automotive --platform mcu` | 42 skills incl. `autosar`, `safety`, `mcu`, `rtos` |
| Drone autopilot on SoC + Linux | `engage --domain robotics --platform soc` | 37 skills incl. `robotics`, `embedded-linux`, `edge-ai` |
| Industrial gateway on MPU + Zephyr | `engage --domain industrial --platform mpu` | slice incl. `security`, `embedded-linux`, `mpu` |
| Satellite payload (custom RTOS) | `engage --domain aerospace --platform mpu` | slice incl. `validation`, `fault-injection` |

Process skills (`requirements`, `architecture`, `traceability`, `evidence`,
…) are tagged `"all"` in the facets registry, so they appear in **every**
slice — deliberately: every project needs requirements and traceability.

---

## 6. Interfaces: REST, MCP, A2A, Python SDK

One implementation (`packages/axiom_sdk`) sits behind all five interfaces —
they always agree (a test enforces this, see `tests/test_interfaces.py`).

### 6.1 REST (needs `axiom serve` running)

```powershell
# Health + inventory
curl http://127.0.0.1:8765/v1/status

# Skill slice for your project
curl -X POST http://127.0.0.1:8765/v1/engage `
  -H "Content-Type: application/json" `
  -d '{"domain":"automotive","platform":"mcu"}'

# Execution plan
curl -X POST http://127.0.0.1:8765/v1/run `
  -H "Content-Type: application/json" `
  -d '{"request":"add watchdog driver","domain":"automotive","platform":"mcu"}'

# Fix / feature plans
curl -X POST http://127.0.0.1:8765/v1/fix -H "Content-Type: application/json" -d '{"issue_id":"BOOT-123"}'
curl -X POST http://127.0.0.1:8765/v1/feature -H "Content-Type: application/json" -d '{"feature_id":"OTA-DELTA"}'

# Discovery
curl http://127.0.0.1:8765/v1/skills
curl http://127.0.0.1:8765/v1/skills/mcu
curl http://127.0.0.1:8765/v1/profiles
```

Missing body fields get HTTP 400 with an `{"error": ...}` message
(e.g. `missing 'request'`); unknown skills get 404 (`unknown skill: xyz`).

### 6.2 MCP (needs an MCP client; no server process to manage)

Point the client at `axiom mcp` via `clients/mcp.json` (see §3.6). Tools:
`engage`, `run_plan`, `get_status`, `plan_fix`, `plan_feature`,
`read_skill`, `list_skills`, `list_profiles`. Example tool call the client
sends over stdio:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"engage","arguments":{"domain":"automotive","platform":"mcu"}}}
```

### 6.3 A2A (needs `axiom serve` running)

Task envelope at `POST /v1/a2a/tasks`, agent card at
`GET /.well-known/agent.json`:

```powershell
curl -X POST http://127.0.0.1:8765/v1/a2a/tasks `
  -H "Content-Type: application/json" `
  -d '{"message":"add watchdog driver","domain":"automotive","platform":"mcu"}'
```

Response: `{"taskId":"axiom-...","status":"completed","agent":"axiom-embedded","artifact":{...plan...}}`.

### 6.4 Python SDK (no server needed)

```python
from axiom_sdk import (engage_skills, run_plan, plan_fix, plan_feature,
                       get_status, read_skill, list_skills, list_profiles)

engage_skills(domain="robotics", platform="soc")   # dict with skills/profiles/context_files
run_plan("tune planner latency", "robotics", "soc") # plan dict
plan_fix("NAV-77", "robotics", "soc")               # 10-step envelope
plan_feature("VOXL-MAP", "robotics", "soc")         # 9-step envelope
get_status()                                        # health dict
read_skill("mcu")                                   # SKILL.md text (KeyError if unknown)
list_skills()                                       # ["ai-validation", ..., "validation"]
list_profiles()                                     # ["automotive-mcu", "skill-update-profile", ...]
```

Add `packages/` to `sys.path` (or `pip install -e .` and import from the
repo) — there is no published PyPI package yet.

---

## 7. AI-client setup

| Client | How to connect | Config / doc |
|--------|---------------|--------------|
| Claude Code / Claude Agent Skills | Copy skills (`install_skills.py --harness claude`) or MCP | `docs/using-skills.md` |
| opencode | Copy skills (`--harness opencode`) or MCP server entry | `clients/mcp.json` |
| Muse | Skills folder or MCP (MCP irregular on some plans — skills folder is the safe path) | `clients/COPILOT.md` |
| Cursor | Skills folder or MCP server entry | `clients/CURSOR.md` |
| VS Code (any extension host) | MCP server entry, or REST while `serve` runs | `docs/client-matrix.md` |
| Codex | Copy skills (`--harness codex`) | `docs/using-skills.md` |
| Antigravity | Copy skills (`--harness antigravity`) | `docs/using-skills.md` |
| Custom AI / local LLM | REST (`serve`) or SDK import | §6.1 / §6.4 |
| Web app | REST (`serve`) | §6.1 |
| Terminal / scripts | CLI directly | §3 |

Detailed per-client notes live in `docs/using-skills.md` (skills install),
`docs/client-matrix.md` (11 clients × 5 interfaces), `clients/COPILOT.md`,
and `clients/CURSOR.md`.

---

## 8. Interface × client matrix

Which interface to use with which client (full table: `docs/client-matrix.md`):

| Client | CLI | REST | MCP | A2A | SDK |
|--------|:---:|:----:|:---:|:---:|:---:|
| Terminal / scripts | ✅ | ✅ | — | — | ✅ |
| Web app | — | ✅ | — | ✅ | — |
| Custom AI / local LLM | — | ✅ | ✅ | ✅ | ✅ |
| Claude / GPT / Gemini agents | ✅ slice-install | ✅ | ✅ | ✅ | — |
| Copilot | ✅ slice-install | ✅ | ⚠️ plan-dependent | — | — |
| Cursor / VS Code | ✅ slice-install | ✅ | ✅ | — | — |
| opencode / Codex / Antigravity | ✅ slice-install | ✅ | ✅ | — | — |

✅ = supported · ⚠️ = works with caveats (see client doc) · — = not applicable.

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `cp1252` / `UnicodeEncodeError` on Windows | `chcp 65001`, then re-run |
| `axiom` command not found | Use `python -m axiom_cli …`, or re-run `pip install -e .` and check `PATH` |
| `repo validate` FAILs | Run `python -m axiom_cli repo validate` output lists the file; usually a hand-edited manifest — compare with a sibling skill's `manifest.yaml` |
| `serve` port in use | `axiom serve --port 8931` |
| REST returns `missing 'request'` (400) | The POST body needs the named field — see §6.1 examples |
| REST returns `unknown skill: xyz` (404) | Check the id against `axiom engage` output or `GET /v1/skills` |
| MCP client can't spawn server | Check the entry shape for your client (generic `{command, args}` vs OpenCode `{type: "local", command: [argv...]}` — see §3.6); test manually with `axiom mcp` (it waits on stdin — `Ctrl+C` to quit). The server echoes the client's `protocolVersion` in its `initialize` response. |
| Tests fail after editing | `python -m pytest -q` shows which; interface tests assert all five surfaces agree, so update SDK first, then re-run |

---

*Standards cited across skills: ISO 26262:2018, IEC 61508 Ed.2.0, DO-178C/DO-254,
MISRA C:2025 / C++:2023, AUTOSAR R24-11/R25-11, Yocto 6.0/5.0 LTS, ROS 2
Kilted/Jazzy/Humble, SPDX, UNECE R155/R156 — each with clause and source URL
in the skill's §2 table. Architectural decisions: `docs/adr/0001`–`0006`.*
