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
python -m axiom_cli doctor
python -m axiom_cli profile validate profiles/generic-embedded.yaml
python -m axiom_cli analyze .
python -m axiom_cli context select --root examples/brownfield-c-project/source/main.c --hops 2
python -m axiom_cli graph build examples/brownfield-c-project --output .axiom/index.json
python -m axiom_cli impact examples/brownfield-c-project/project.yaml
```

## AI clients

The repository contains shared agent instructions and integration contracts for AI clients. Root `AGENTS.md` is the portable project contract. GitHub Copilot additionally consumes `.github/copilot-instructions.md` and path-specific instruction files. OpenCode uses the repository `AGENTS.md` and `opencode.json` instruction list.

## Safety and certification boundary

AxiomEmbedded provides engineering process automation and reference checks. A passing check is not a certification result and must not be represented as proof of compliance, safety integrity, security certification, or airworthiness. The adopting project must determine applicable editions, objectives, independence requirements, and evidence with qualified personnel and authorised tools.

## Licensing
# Third-party notices

The content is original and licensed under Apache-2.0. External projects and standards listed under `references/` are references only and are not bundled, vendored, or incorporated.
The active platform uses the Apache-2.0 licence. AxiomEmbedded  migration is supported from an external source tree; the legacy starter is not vendored. Third-party standards text is not redistributed.
