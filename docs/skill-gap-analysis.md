# Skill Gap Analysis (reference-inspired, original content only)

No reference text was copied. Coverage comparison only:

| Reference domain | AxiomEmbedded coverage | Gap | Planned AxiomEmbedded skill | Original angle | Priority |
|---|---|---|---|---|---|
| AUTOSAR Classic RTE/OS/BSW/COM | autosar, mcu, rtos, automotive-networks | No per-area workflows (RTE design, OS config, COM stack, BSW integration) | axiom-autosar-classic-architecture, axiom-autosar-classic-bsw-integration, axiom-autosar-rte-design, axiom-autosar-os-config, axiom-autosar-com-stack | ARXML-inventory + config-delta + validation-matrix workflows | P0 |
| AUTOSAR Adaptive | autosar (thin) | No ara::com/EM/SM/PHM/persistency/time-sync diagnostics workflow | axiom-autosar-adaptive-deployment | Service-manifest + deployment-checklist method | P0 |
| CAN/LIN/FlexRay/Ethernet | automotive-networks | No DBC/design-rule + SOME/IP design workflows | axiom-can-network-design, axiom-can-stack-integration, axiom-automotive-ethernet-someip | Bus-load/timing + stack-config checkers | P0 |
| Diagnostics UDS/DoIP/OBD | automotive-diagnostics (deep, v1.3.0) | DoIP/test-plan/traceability as reusable generators | axiom-diagnostics-uds, axiom-diagnostics-doip | Extract-driven matrix + script validators | P0 |
| Safety ISO 26262 | safety | No HARA/safety-goal/FSR-TSR/FMEA-FTA workflow | axiom-functional-safety | Evidence-structure + review-gate method | P0 |
| Cybersecurity ISO 21434 | automotive-cybersecurity, security | No TARA/secure-boot/secure-diag/key-mgmt workflow | axiom-vehicle-cybersecurity | Threat-model template + gate checks | P0 |
| ADAS/AD | adas | No perception-pipeline/validation KPI workflow | axiom-adas-perception-pipeline, axiom-adas-validation | Interface-contract + replay-KPI method | P1 |
| BMS | none | Full gap | axiom-bms-design, axiom-bms-diagnostics | Contactor/thermal/fault + HIL test design | P1 |
| V2X/connectivity | none | Full gap | axiom-v2x-communication | Message-model + latency/security checks | P1 |
| Zonal/SDV | automotive-middleware | No zonal/service-oriented/TSN/update workflow | axiom-zonal-architecture | Compute-allocation + update-strategy method | P1 |
| Release/ASPICE | release, automotive-spice | No release-readiness gate workflow | axiom-automotive-release-readiness | Evidence-package gate | P1 |
| Embedded/RTB | hardware-bringup, rtos, debugging, performance | No bringup/trace/memory/test/HIL workflows as skills | axiom-embedded-firmware-bringup, axiom-rtos-architecture, axiom-trace-analysis, axiom-memory-and-performance-analysis, axiom-test-automation, axiom-hil-test-planning | Deterministic scripts + checklists | P1 |
| Cross-domain | architecture, code-review, traceability | No contract/static-analysis-triage/CI-ADR-debt workflows | axiom-platform-architecture-review, axiom-robotics-system-integration, axiom-industrial-control-review, axiom-aerospace-defense-safety-review | Reusable review/test/ADR templates | P1 |
