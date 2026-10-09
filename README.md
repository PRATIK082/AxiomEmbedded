# AxiomEmbedded

**Open AI-Native Engineering Platform for Embedded & Cyber-Physical Systems**

AxiomEmbedded is an open, domain-neutral engineering platform for building, analysing, testing, validating, documenting, maintaining, and evolving embedded products. It connects engineering artifacts, lifecycle workflows, domain/platform profiles, machine-readable rules, AI agents, tool execution, traceability, context optimization, and engineering evidence.

## The central architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    AI ENGINEERING AGENTS                    │
├─────────────────────────────────────────────────────────────┤
│ Requirement │ Architecture │ Code │ Test │ Review │ Debug  │
├─────────────────────────────────────────────────────────────┤
│                    V-CYCLE ENGINE                           │
├─────────────────────────────────────────────────────────────┤
│ Requirements │ Design │ Implement │ Verify │ Validate      │
├─────────────────────────────────────────────────────────────┤
│                 ENGINEERING KNOWLEDGE BASE                   │
├─────────────────────────────────────────────────────────────┤
│ Standards │ Rules │ Checklists │ Templates │ Patterns       │
├─────────────────────────────────────────────────────────────┤
│                 DOMAIN SKILL PACKS                           │
├─────────────────────────────────────────────────────────────┤
│ Automotive │ Aerospace │ Defense │ Industrial │ Robotics     │
├─────────────────────────────────────────────────────────────┤
│                PLATFORM SKILL PACKS                         │
├─────────────────────────────────────────────────────────────┤
│ MCU │ MPU │ MPSoC │ RTOS │ Linux │ Bare-metal │ FPGA        │
├─────────────────────────────────────────────────────────────┤
│                 TOOL / AUTOMATION LAYER                      │
├─────────────────────────────────────────────────────────────┤
│ Python │ CMake │ Git │ CI/CD │ GCC │ Clang │ QEMU │ GDB     │
└─────────────────────────────────────────────────────────────┘
```

## What it covers

**Domains:** generic embedded, automotive, aerospace, space, defense, industrial, robotics, medical, energy, rail, marine, telecom, IoT, consumer and semiconductor.

**Compute:** MCU, MPU, SoC, MPSoC, FPGA, GPU, NPU and DSP.

**Execution:** bare-metal, RTOS, FreeRTOS, Zephyr, NuttX, AUTOSAR OS, Embedded Linux and mixed systems.

**Languages:** C, C++, Rust, Python and assembly.

**AI:** edge AI, TinyML, computer vision, model optimisation, quantisation, deployment and inference validation.

**Lifecycle:** greenfield, V-model, iterative, incremental, Agile, brownfield recovery, maintenance, defect fix, feature change, migration, security patch and release.

## Core idea

```text
                         ┌───────────────────────┐
                         │       USERS           │
                         │ Engineers / Teams     │
                         └───────────┬───────────┘
                                     │
                     ┌───────────────┼────────────────┐
                     ↓               ↓                ↓
                 Copilot          OpenCode         Web/CLI
                     │               │                │
                     └───────────────┼────────────────┘
                                     ↓
                          ┌────────────────────┐
                          │ Agent Interop      │
                          │ MCP / A2A / API    │
                          └─────────┬──────────┘
                                    ↓
                          ┌────────────────────┐
                          │ AGENT RUNTIME      │
                          └─────────┬──────────┘
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
               Engineering       Domain           Tool
                 Agents          Agents           Agents
                    │               │               │
                    └───────────────┼───────────────┘
                                    ↓
                          ┌────────────────────┐
                          │ CONTEXT ENGINE     │
                          │ Graph + Index      │
                          └─────────┬──────────┘
                                    ↓
            ┌───────────────────────┼────────────────────────┐
            ↓                       ↓                        ↓
       Requirements            Architecture              Code
            │                       │                        │
            └───────────────────────┼────────────────────────┘
                                    ↓
                          ┌────────────────────┐
                          │ WORKFLOW ENGINE    │
                          └─────────┬──────────┘
                                    ↓
                   V / Agile / Brownfield / Maintenance
                                    ↓
                          ┌────────────────────┐
                          │ VERIFICATION       │
                          │ TEST / ANALYSIS    │
                          └─────────┬──────────┘
                                    ↓
                          ┌────────────────────┐
                          │ EVIDENCE ENGINE    │
                          └─────────┬──────────┘
                                    ↓
                               Git / CI / PR
```

The **artifact graph is the engineering source of truth**. Documents, reports and AI responses are derived views or evidence; agents should not treat a chat transcript as the authoritative project state.

## Why it exists

Many embedded projects begin from different points. A new product may start at requirements; a mature product may already be in implementation, verification or maintenance. AxiomEmbedded therefore models the entry point explicitly and supports both greenfield and brownfield workflows.

## Quick start

```bash
pipx install axiom-embedded
axiom doctor
axiom
```

Without installing (source checkout):

```bash
python -m axiom_cli doctor --skip-tests
python -m axiom_cli profile validate profiles/generic-embedded.yaml
python -m axiom_cli analyze .
python -m axiom_cli context select --root examples/brownfield-c-project/source/main.c --hops 2
python -m axiom_cli graph build examples/brownfield-c-project --output .axiom/index.json
python -m axiom_cli impact examples/brownfield-c-project/project.yaml
```

## AI clients

Install the Axiom pack into any project (merges, never clobbers):

```bash
axiom install --client opencode   # .opencode/agents, .opencode/skills, opencode.json (mcp)
axiom install --client claude     # .claude/agents, .claude/skills, .mcp.json
axiom install --client codex      # .codex/config.toml (mcp_servers.axiom-embedded)
axiom install --client gemini     # .gemini/settings.json + GEMINI.md
axiom install --client copilot    # .github/copilot-instructions.md
```

Add `--global` for user-level config (`~/.config/opencode`, `~/.claude`,
`~/.codex`, `~/.muse`; Copilot stays per-repository). Regenerate the
checked-in client files after editing `skills/` or `agents/`:

```bash
python scripts/sync_clients.py        # regenerate
python scripts/sync_clients.py --check # CI freshness gate
```

The repository contains shared agent instructions and integration contracts for AI clients. Root `AGENTS.md` is the portable project contract. GitHub Copilot additionally consumes `.github/copilot-instructions.md` and path-specific instruction files. OpenCode consumes `.opencode/agents/`, `.opencode/skills/`, `.opencode/commands/` (`/axiom-*`), the `axiom-policy` plugin (`.opencode/plugins/`), and the `mcp.axiom` entry in `opencode.json`. Every `axiom` command is also an MCP tool over stdio (`axiom mcp`, 19 tools, JSON schemas); `clients/mcp.json` holds a portable server entry.

Live OpenCode runtime (isolated config under `~/.axiom/opencode`, never touches
the user's own OpenCode setup; see `docs/OPENCODE_COMPAT.md` for the tested
version range and `docs/OPENCODE_LAUNCHER.md` for details):

```bash
axiom oc tui                # interactive OpenCode TUI with the Axiom MCP attached
axiom oc run "add driver"   # one-shot headless run (flags: --model --agent --dir --format)
axiom oc research "question" # research-framed headless run via the explore agent
axiom oc run "task" --dry-run # print argv/env without executing
```

Deep research without leaving the terminal (planner → searchers →
verifier → synthesizer with citations; `auto` uses OpenCode subagents when
available, otherwise the keyless local backend):

```bash
axiom research "ISO 26262 automotive safety" --backend local
axiom research "question" --format markdown --output report.md
```

## Compatibility

| Component | Supported |
|---|---|
| Python | ≥ 3.11 (PyYAML only; pytest for tests) |
| OpenCode (live `axiom oc` / research) | v1, tested 1.18.31–1.18.35; v2 fails closed (see `docs/OPENCODE_COMPAT.md`) |
| Install | `pipx install axiom-embedded` (or `pip install axiom-embedded`) |
| AI clients | opencode / claude / codex / gemini / copilot via `axiom install --client` |


## Safety and certification boundary

AxiomEmbedded provides engineering process automation and reference checks. A passing check is not a certification result and must not be represented as proof of compliance, safety integrity, security certification, or airworthiness. The adopting project must determine applicable editions, objectives, independence requirements, and evidence with qualified personnel and authorised tools.

## Licensing
# Third-party notices

The content is original and licensed under Apache-2.0. External projects and standards listed under `references/` are references only and are not bundled, vendored, or incorporated.
The active platform uses the Apache-2.0 licence. AxiomEmbedded  migration is supported from an external source tree; the legacy starter is not vendored. Third-party standards text is not redistributed.
