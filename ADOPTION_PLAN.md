# Skill Content Enhancement Plan — Adopted from Deep Research

## Research Summary (6 subagents, 100+ sources)

### Sources
- 50+ GitHub repos with embedded/automotive/aerospace/robotics/industrial skills
- 25+ AI agent skill format sources (agentskills.io, Claude, Cursor, Copilot, Windsurf, OpenCode, Gemini, Codex)
- 24+ V&V authoritative sources (Unity, Ceedling, GoogleTest, Labgrid, pytest-embedded, Renode, RF, ISO 26262, DO-178C, IEC 61508)
- 35+ MCP server/skill collections (Glama, MCP.so, Smithery, 19 embedded MCP servers)
- 21+ coding assistant rule examples (.cursorrules, .clinerules, copilot-instructions, AGENTS.md)
- 30+ industry standards sources (ISO 26262, DO-178C, IEC 61508, MISRA C, AUTOSAR, IEC 62304)

### Key Patterns to Adopt (NO copy-paste, independently adapted)

#### P0 — Universal skill quality (apply to ALL 277 skills)
1. **Progressive disclosure**: SKILL.md < 500 lines, references one level deep, scripts/ for deterministic steps
2. **Copyright-safe standards**: Rule IDs + clause numbers + paraphrased rationale + compliant/non-compliant examples. Never normative text.
3. **Builder + reviewer pairs**: Every artifact-producing skill gets a confirmation reviewer
4. **Impact tiers**: CRITICAL / HIGH / MEDIUM / LOW for all rules and checks
5. **Prefix-based rule taxonomy**: misra-, autosar-, safety-, realtime-, comm-, security-, iso26262-, iec61508-, do178c-, iec62304-

#### P1 — V&V skill enhancement (apply to test/validation/safety skills)
6. **Sanitizer gates**: ASan/UBSan/LSan + SARIF reports in unit-test, test-automation
7. **Fuzzing lifecycle**: Coverage-guided fuzzer harness, corpus management, crash triage
8. **Property-based testing**: For protocol parsers and arithmetic
9. **Mutation testing**: For critical code paths
10. **Death tests**: For error-handling paths (GoogleTest pattern)
11. **Multi-DUT testing**: Synchronized multi-DUT test logic with per-device options
12. **Cloud emulation**: Wokwi/esp-emu for hardware-free CI
13. **Flash caching**: Hash-based skip reflash
14. **Panic/core-dump decoding**: Automated backtrace decode on failure
15. **Labgrid architecture**: Coordinator/exporter/RemotePlace, ManagedResources/udev, Strategy pattern for boot states
16. **Keyword layered architecture**: Protocol-level Python libs + domain keywords (Robot Framework)
17. **RF remote execution**: pabot parallel, Rebot merge, remote servers
18. **Firmware provisioning in CI**: Automated flash before system tests
19. **Co-simulation**: Verilator/SystemC/FPGA for SIL
20. **RESD sensor replay**: Deterministic HIL sensor data replay
21. **Secure boot validation**: eFuse timing, QEMU encrypted-flash sim, voltage-glitch fault injection
22. **PSA/SESIP validation**: NIST SP 800-193 resiliency checks

#### P2 — Agent & architecture enhancement
23. **Three-zone autonomy**: Core/evidence (AI no access), gray (AI assistant + HITL), non-critical (AI unrestricted) — encode in AGENTS.md
24. **Deviation management**: Rule ID, reason, file, approver, date (Straion pattern)
25. **Knowledge-base layering**: rules/ (enforceable), knowledge-base/ (reference), skills/ (procedures), agents/ (personas), commands/ (slash), workflows/ (end-to-end), hooks/ (safety gates), tools/ (adapters)
26. **Builder + reviewer pairs**: Every artifact-producing skill paired with confirmation reviewer
27. **Cross-tool portability**: AGENTS.md as canonical, thin wrappers for CLAUDE.md, .cursor/rules, etc.
28. **Self-updating meta-rule**: Rules updated on bug fixes, separate ADRs from lessons
29. **Glob-scoped activation**: Rules load only when editing matching files
30. **Audit tooling**: Detect bloat, duplication, dead imports in instruction files

#### P3 — Embedded-specific guidance (from coding assistant rules research)
31. **Hardware safety checklists**: GPIO, ISR, DMA, volatile discipline, no heap, no exceptions/RTTI
32. **Build/flash discipline**: Clean rebuild, verify target board, check serial port, pin library versions
33. **Testing discipline**: Host unit tests, HIL verification, two-board cross-device testing
34. **Memory constraints**: Static buffers, const lookup tables, fixed-point, stack usage checks
35. **Peripheral discipline**: DMA variants, HAL return values, RTOS-agnostic BSP

### Implementation Strategy

Apply patterns to skills by category:
- **Test/validation skills** (unit-test, integration-test, system-test, test-automation, fault-injection, sil-hil-bridge, bus-protocol-validation, axiom-validation-levels, axiom-validation-orchestrator, axiom-hw-interface-control, axiom-firmware-lifecycle, axiom-sil-hil-bridge): Apply P1 patterns
- **Safety/security skills** (safety, security, axiom-safety-*, axiom-security-*, axiom-threat-model, axiom-vehicle-cybersecurity): Apply P0 + P2 patterns
- **All skills**: Apply P0 universal patterns (progressive disclosure, copyright-safe, impact tiers)
- **Agents**: Apply P2 patterns (three-zone autonomy, builder+reviewer)
- **Root AGENTS.md**: Apply P2 (three-zone autonomy, knowledge-base layering)

### Execution Plan
Use parallel subagents by skill category. Each subagent:
1. Reads the current skill content
2. Applies relevant patterns from this plan
3. Writes updated SKILL.md, checklists, references, templates
4. Validates with validate_skill_doc
5. Does NOT create new skills

### Cross-Verification
- Positive: patterns correctly applied, validate_skill_doc passes
- Negative: no normative text copied, no new skills created, no broken references
- Cross: pipeline --check green, pytest green after all changes
