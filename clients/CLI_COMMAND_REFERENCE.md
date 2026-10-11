# AxiomEmbedded CLI — Command Reference + Project Setup Guide

Branch: `update_frame_v1` (built on `main`). Every example below was run
against this tree. CLI entry: `python -m axiom_cli ...` (or `axiom ...`
after `pip install .`).

> Note: the `skills`, `packs`, and `compose` command groups exist only on
> the `skill-frmeworkupdate` branch. On this branch, skill discovery runs
> through `engage` + `route` + `run` below.

## 1. Health and project checks

| Command | Use | Example |
|---|---|---|
| `version` | Print version | `python -m axiom_cli version` → `axiom-embedded 0.2.0` |
| `doctor` | Env + repo + test health | `python -m axiom_cli doctor` (add `--skip-tests` for a fast check) |
| `repo-validate` / `repo validate` | Required-files check | `python -m axiom_cli repo-validate` |
| `status [--format json]` | Terminal dashboard: health, next action | `python -m axiom_cli status` |

Missing files now return friendly JSON (`{"status":"error","message":...}`,
exit 2) instead of tracebacks — fixed on this branch for
`profile validate` and `workflow plan`.

## 2. Skill discovery and planning (the core loop)

```bash
# What skills/profiles fit this project?
python -m axiom_cli engage --domain automotive --platform mcu
# automotive+mpu engages 76 skills incl. all 35 axiom-* (was 71 before domains=[all] skills)

# Route a plain-language request to the owning agent
python -m axiom_cli route "review the CAN stack integration"

# Plan-then-execute plan for a task (model-agnostic; host supplies the model)
python -m axiom_cli run "bring up CAN on the gateway ECU" --domain automotive --platform mcu

# Targeted 9-step feature / 10-step defect plans
python -m axiom_cli feature F-001 --domain automotive --platform mcu
python -m axiom_cli fix ISSUE-12 --domain automotive --platform mcu
```

## 3. Project lifecycle: development vs maintenance setup

Use `stage` first — it detects the lifecycle stage from evidence + profile:

```bash
python -m axiom_cli stage . --profile configs/project.yaml
```

**New development project:**

1. `status` — confirm repo health baseline.
2. `engage --domain <d> --platform <p>` — load the right skill slice.
3. `workflow plan --profile configs/project.yaml --entry <phase>` — resolve the starting workflow phase.
4. `run "<objective>" --domain <d> --platform <p>` — plan-then-execute each work item.
5. `feature <id>` per feature for the 9-step plan with approvals.

**Maintenance-phase project:**

1. `stage .` — confirm it reports a late-lifecycle stage (evidence-driven, not assumed).
2. `engage` with the same domain/platform — keeps the skill surface identical so regressions are comparable.
3. `fix <issue-id>` per defect — 10-step plan with impact + approval gates; never bypass a gate to make CI green.
4. `status` after each fix — dashboard shows whether health moved.
5. `research "<question>" --backend local` for offline codebase investigation (see §5).

## 4. Context, impact, graph

```bash
python -m axiom_cli context select --root skills/autosar --hops 2
python -m axiom_cli impact configs/project.yaml
python -m axiom_cli graph build . --output .axiom/index.json
python -m axiom_cli analyze .
```

## 5. Research (offline-safe)

```bash
python -m axiom_cli research "how is UDS configured?" --backend local
```

`--backend auto` may hang waiting on network providers; offline, always pass
`--backend local`. Output: `{status, backend_used, answer, citations}`.

## 6. Serving (MCP / REST / OpenCode launcher)

```bash
python -m axiom_cli mcp                    # MCP over stdio, 21 tools (any MCP client)
python -m axiom_cli serve --port 8765      # REST + A2A; GET / serves the HTML dashboard
python -m axiom_cli oc run "do X"          # OpenCode launcher (isolated config; --dry-run to preview)
python -m axiom_cli oc tui                 # interactive TUI
```

## 7. Install / update / uninstall (client configs)

```bash
python -m axiom_cli install --client opencode --path <project-dir>
python -m axiom_cli install --client claude --global --domains automotive,robotics
```

Clients: `opencode|claude|codex|gemini|copilot`. `--global` writes user-global
config; otherwise project scope. Domain filtering (`--domains`) is a
`skill-frmeworkupdate`-branch capability; on this branch install copies the
full skill set. Full lifecycle (map → update → unmap) is covered in
`clients/INSTALL_TEST_GUIDE.md`:

```bash
python -m axiom_cli update --client opencode --path <project-dir>
python -m axiom_cli uninstall --client opencode --path <project-dir>
```

## 8. Exit-code contract (for scripts and CI)

- `0` — ok (`status: ok` in JSON output).
- `1` — failed check / validation error / unknown tool.
- `2` — missing input file (friendly JSON, no traceback).

## 9. Auto skill selection + autonomy ladder

### 9.1 Does `engage` auto-analyze, or must the user set domain/platform?

Three paths, most-manual first:

1. **Explicit** — you set it: `engage --domain automotive --platform mcu`.
   Deterministic filter over `registries/skill-index.json`; no guessing.
2. **Prompt-text detection** — `run "<request>"` without `--domain` calls
   `detect_domain()` (distinctive keywords only: `uds`, `autosar`, `asil`,
   …; generic words like `can`/`code` deliberately excluded). Output records
   `domain_source: explicit|detected|none` so you can audit which path fired.
3. **Project-file detection (new)** — `engage --auto [PATH]` scans the
   project's own files (extensions like `.dbc`/`.arxml`/`.urdf`, filenames
   like `package.xml`, bounded keyword sniffs of `CMakeLists.txt`/`Kconfig`)
   and returns `{domain, platform, os, confidence, signals[]}` plus the
   engaged skill list. Same via MCP: `engage` tool with `auto_path`.
   No network, no model, capped walk (2000 files, 4 KiB sniffs); every vote
   is listed in `signals[]` so the guess is auditable.

Recommendation: CI/scripts → path 1 (pinned, reproducible). Interactive
agent sessions → path 3, falling back to 1 when `confidence < 0.5`.

### 9.2 Linking this to opencode|claude|codex|gemini|copilot

`install --client <c>` does two things per client: (a) copies the generated
agent/skill files, (b) registers the MCP server. After that each client
consumes skills differently:

| Client | Skills arrive as | Auto behavior |
|---|---|---|
| opencode | `.opencode/skills/*/SKILL.md` + MCP | Auto-discovers skills; `axiom mcp` tools callable |
| claude | `.claude/skills/*/SKILL.md` + MCP | Same file-copy model |
| codex | `AGENTS.md` + MCP | Reads AGENTS.md automatically; skills via MCP `engage`/`run_plan` at runtime |
| gemini | `GEMINI.md` + MCP | Instruction file + MCP tools |
| copilot | `.github/copilot-instructions.md` + MCP | Agent Mode reads instructions; skills via MCP |

So "linking" = install once per client, then every client resolves skills at
runtime through the same MCP tools (`engage`, `route`, `run_plan`,
`read_skill`). One source of truth, five consumers.

### 9.3 Autonomy levels — what to use when

- **L0 human-in-the-loop** (default): every write-capable surface is
  dry-run-first (`skills run` without `--apply`, MCP `apply=false`).
  The agent proposes; the human applies. Use for safety/security-relevant work.
- **L1 human-on-the-loop**: agent runs with `--apply`, but
  `APPROVAL_REQUIRED_FOR` (`git push`, `release`, destructive/safety/security
  changes) still blocks without approval, and `status`/`doctor` verify after.
  Human supervises, intervenes on flags.
- **L2 agentic session**: `axiom oc run "<task>"` (or the client's own agent
  with MCP enabled). Agent loops plan→implement→verify inside one session;
  L0/L1 gates still apply per action.
- **L3 orchestration**: split by skill directory (one agent = one
  `skills/<id>/` area), merge only when `pytest` + `doctor` are green.
- **L4 self-loop to done**: harness loop around axiom primitives —
  `run` (plan) → apply → `pytest`/`doctor` → `status`, repeat until the
  dashboard shows no NEEDS ATTENTION. Axiom provides the loop *body*
  (deterministic checks with JSON status); the *loop itself* lives in the
  client harness, with L1 approval gates untouched so "finish the task" can
  never silently push, release, or bypass a safety gate.
