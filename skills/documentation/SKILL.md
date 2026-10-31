---
name: documentation
description: Docs-as-code, versioned-with-product docs, tested examples. Use when writing manuals, API docs, or runbooks.
version: 1.3.0
domains: [all]
platforms: [all]
axiom:
  dotted_name: axiom.legacy.documentation
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills:
  - axiom-architecture-decision-records
  checklists:
  - checklists/documentation-checklist.md
---

# Documentation skill

Technical documentation engineers and auditors actually use: architecture
records, interface documents, user and service manuals, and the doc pipeline
that keeps them correct, versioned, and reviewed alongside code.

## 1. Purpose and scope

**Purpose.** Deliver documentation that is accurate at the release it
describes, traceable to the system it documents, and maintained with the same
discipline as code.

**In scope.** Document types (architecture, ICDs, API references, user/service
manuals, safety-manual appendices), docs-as-code pipeline, review and approval
workflows, versioning per release, and readability/accuracy standards.

**Non-goals.** Marketing content and in-code comments (see
`implementation` §3). Ends at a reviewed documentation set released with the
product.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | ISO/IEC/IEEE 26511 Requirements for managers of information | 2018 | Documentation management across the life cycle | `https://www.iso.org/standard/70872.html` |
| 2 | ISO/IEC/IEEE 26514 Design and development of user documentation | 2022 | User-doc processes and quality criteria | `https://www.iso.org/standard/75888.html` |
| 3 | ISO 26262-10 Guidelines | 2018 | Documentation structure expectations for safety work products | `https://www.iso.org/standard/68392.html` |

## 3. Rules

1. **Docs as code.** Sources in version control, reviewed in the same
   merge-request flow as code, built by CI; generated artifacts (PDFs, sites)
   are reproducible from tagged sources. Wiki-only knowledge is tribal
   knowledge — migrate or lose it.
2. **Versioned with the product.** Each release ships its doc set; docs state
   the exact product version and baseline they describe. Stale version
   references are defects found by CI link/version checks, not by readers.
3. **Interfaces documented once.** APIs, protocols, and ICDs have a single
   normative source (generated from code/contracts where possible); duplicated
   interface descriptions in prose docs drift and are forbidden as normative.
4. **Safety-relevant docs reviewed.** Safety manuals, integration instructions,
   and assumptions-of-use documents follow the integrity level's independence
   rules (`safety` §6) — a safety manual reviewed only by its author is not
   evidence.
5. **Tested examples.** Code samples and procedures in docs are executed by CI
   (doctest-style or rig-run); untested examples rot and mislead.

## 4. Release gates (blocking)

1. Doc set built from the release tag; version references verified by CI.
2. Interface docs generated from normative sources, no prose duplicates.
3. Safety/assumption-of-use docs reviewed with required independence.
4. Examples and procedures executed green in CI.

## 5. Verification of this skill (Phase 4 gate)

- Standards carry number + version + clause + URL (§2).



## 7. Embedded firmware documentation levels and templates

### 7.1 Documentation levels
| Level | Content | When Generated |
|-------|---------|----------------|
| L1 â€” Project | README, Architecture, Build, Hardware, Directory Structure | New project |
| L2 â€” Module | Per-module design docs | New module created |
| L3 â€” Interface | Interface contract docs | New interface created |
| L4 â€” RTOS/ISR | TaskDesign, ISRDesign, EventFlow | `osThreadNew` or `IRQHandler` detected |
| L5 â€” Control | ControlLoop, StateMachine, Estimator | State machine enum or control structures detected |

### 7.2 Project-level documentation (L1)
Generate `README.md`, `docs/Architecture.md`, `docs/Build.md`, `docs/Hardware.md`, `docs/DirectoryStructure.md`.

README must contain: Project Overview, Features, Hardware Platform, Build Instructions, Flash Instructions, Project Structure, Software Architecture, Dependencies, License.

Architecture doc must describe the layer model with ASCII dependency diagram:
```
app/ â†’ module/ â†’ interface/ â†’ bsp/ â†’ platform/
```

Hardware doc must include a resource table (Peripheral, Interface, Target, Purpose) when GPIO/UART/SPI/I2C/CAN/PWM/ADC are referenced.

### 7.3 Module-level documentation (L2)
For each new module, generate `docs/modules/<module>.md` with: Purpose, Responsibilities, Public API, Dependencies, Data Flow, State Machine (if applicable).

### 7.4 Interface documentation (L3)
Every interface documents: Purpose, Public API, Ownership (implemented by BSP, consumed by module), Thread Safety.

### 7.5 RTOS task documentation (L4)
When `osThreadNew()`/`xTaskCreate()` present, generate `docs/TaskDesign.md` with table: Task, Period, Priority, Stack, Responsibility. Plus synchronization primitives table.

### 7.6 ISR documentation (L4)
When `IRQHandler` functions present, generate `docs/ISRDesign.md` with table: Interrupt, Source, Priority, Execution Time, Shared Variables. Plus deferred processing table.

### 7.7 State machine documentation (L5)
When state enum or `switch(state)` present, generate `docs/StateMachine.md` with transition diagram and transition table (Transition, From, To, Condition).

### 7.8 Diagram rules
Prefer ASCII diagrams for architecture and data flow (render inline without external tools). Include architecture, data flow, and task interaction diagrams.

### 7.9 Documentation validation checklist
- [ ] README exists with all required sections
- [ ] Architecture document describes layer model
- [ ] Build instructions documented
- [ ] Hardware resources documented with peripheral table
- [ ] New modules each have a design doc
- [ ] All interfaces document purpose, API, ownership, thread safety
- [ ] RTOS tasks documented (period/priority/stack/responsibility)
- [ ] ISRs documented (source, latency, shared variables, deferred processing)
- [ ] State machines documented (transitions, conditions)
- [ ] Dependency graph and data flow documented
- [ ] Directory structure documented

### 7.10 Auto-fix strategy
When documentation missing: detect undocumented component, generate required doc from templates, link from README TOC, update architecture references.

