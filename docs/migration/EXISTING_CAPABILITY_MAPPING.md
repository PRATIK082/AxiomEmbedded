# Existing Capability Mapping (migration report)

No existing capability was removed or renamed. All 58 legacy skills keep
their IDs, behavior, and registry entries.

| Existing | Disposition | Related axiom-* skill(s) | Notes |
|---|---|---|---|
| autosar | remain tool-skill | axiom-autosar-* (5) | axiom-* are deeper per-area workflows referencing it |
| automotive-diagnostics | remain tool-skill | axiom-diagnostics-uds, axiom-diagnostics-doip | UDS exemplar builds on its generator |
| automotive-networks | remain | axiom-can-*, axiom-automotive-ethernet-someip | — |
| automotive-cybersecurity, security | remain | axiom-vehicle-cybersecurity | — |
| safety | remain | axiom-functional-safety | — |
| adas | remain | axiom-adas-* | — |
| test-automation, unit-test, integration-test, system-test | remain | axiom-test-automation, axiom-hil-test-planning | — |
| rtos, mcu, hardware-bringup, debugging, performance | remain | axiom-rtos-architecture, axiom-embedded-firmware-bringup, axiom-trace-analysis, axiom-memory-and-performance-analysis | — |
| robotics | remain | axiom-robotics-system-integration | — |
| architecture, code-review, traceability, requirements-traceability | remain | axiom-platform-architecture-review | — |
| release, automotive-spice, evidence | remain | axiom-automotive-release-readiness | — |
| all others | remain unchanged | — | listed in catalog.yaml as legacy/production |

Breaking changes: none. New public surface is additive only
(CLI `skills`, MCP skill tools, `packages/skills/*`, new skill dirs).
Required consequential updates (documented, no behavior change):
- Engagement/total count assertions 50→71 and 58→88 (`test_detect`,
  `test_interfaces`, `test_ops`) — catalog grew 58→88 skills.
- Regenerated client files via `python scripts/sync_clients.py` (248 files).
- 3 failing tests are pre-existing on clean HEAD (verified via stash):
  `test_sdk_reexports_ops`, `test_dashboard_html_renders`,
  `test_local_backend_finds_cited_skill_refs` — left untouched.
