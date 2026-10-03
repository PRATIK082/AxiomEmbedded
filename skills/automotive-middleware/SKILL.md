---
name: automotive-middleware
description: SDV middleware selection and integration — ara::com, SOME/IP-SD, DDS, Zenoh, vsomeip, MQTT, TSN, zero-copy IPC, VSS/VSC. Use for service-oriented vehicle platforms, HPC/zone architectures, deterministic Ethernet.
version: 1.2.0
domains: [automotive]
platforms: [mpu, soc, linux, autosar-adaptive]
---

# automotive-middleware — Vehicle middleware / SDV layer

Service-oriented middleware for software-defined vehicles: service discovery,
QoS-bounded pub/sub + request/response over deterministic Ethernet and zero-copy
on-target IPC, with versioned APIs (COVESA VSS/VSC), time-sync, security, OTA-ready
deployment, and observability.

> Relation to `skills/autosar/`: AUTOSAR application/RTE/`ara::com` conformance and the
> Classic↔Adaptive SOME/IP daemon pattern live there. This skill decides **which
> middleware/binding carries each service, with what QoS, schedule, security, and
> versioning policy**. Relation to `skills/embedded-linux/`: BSP/PREEMPT_RT/verified-boot
> mechanics live there; this skill consumes them as deployment prerequisites.

## Objectives

- Select a per-domain middleware binding with recorded rationale and rejection reasons.
- Define versioned service IDLs with back-compat policy, QoS/deadline budgets, TSN
  schedule, time-sync domain, and security profile before any code.
- Integrate Ethernet (SOME/IP-SD, DDS discovery, Zenoh routing) + zero-copy IPC
  (iceoryx-style shared-mem) + deterministic scheduling into one verifiable deployment.
- Prove timing, fault behavior, interoperability (VSS/VSC), and OTA compatibility.

## Prerequisites

- `skills/autosar/` loaded when Classic/Adaptive in scope; `skills/embedded-linux/`
  for HPC/zone controllers (Yocto LTS, PREEMPT_RT, verified boot, A/B OTA).
- Network + compute inventory: topology, link rates, switch Qbv/Qav support, PTP PHYs.
- Domain overlay `domains/automotive/` loaded. C++17-capable toolchain for middleware;
  C++14-constrained public `ara::com` surfaces where Adaptive applies.

## Outcomes

- `requirements/middleware-requirements.md`: MW-xxx service, timing, QoS, compat, security requirements.
- `architecture/middleware-architecture.md`: selection matrix, binding per service,
  IDL/version map, QoS table, TSN config, time-sync domain, security profile, deployment topology.
- `idl/`: pinned service definitions + generated stubs with generator version recorded.
- `src/` bindings + `config/` (vsomeip JSON, DDS XML, Zenoh routers, Qbv schedules, gPTP) + `deploy/`.
- `test/`: timing suites, discovery/interop tests, chaos suites, back-compat suites.
- `evidence/`: every timing/security/compat claim linked to clause, config hash, test result.

## Time estimate

- Selection + architecture: 3–5 days. IDL + binding + deployment: 5–10 days.
  Timing + chaos + interop verification: 5–10 days.

## Resources

- AUTOSAR Adaptive: `https://www.autosar.org/standards/adaptive-platform`
- SOME/IP PRS Doc ID 696: `https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_SOMEIPProtocol.pdf`
- OMG DDS: `https://www.omg.org/spec/DDS/About-DDS/`
- Cyclone DDS: `https://github.com/eclipse-cyclonedds/cyclonedds` — Fast DDS: `https://github.com/eProsima/Fast-DDS`
- Zenoh: `https://zenoh.io/` — iceoryx: `https://eclipse.dev/iceoryx`
- vsomeip: `https://github.com/COVESA/vsomeip`
- COVESA VSS: `https://covesa.dev/vehicle_signal_specification/`
- MQTT: `https://mqtt.org/` — IEEE TSN: `https://1.ieee802.org/tsn/`

## Selection matrix

| Option | Discovery | Best for | Avoid when | Determinism story |
| --- | --- | --- | --- | --- |
| Classic signals (CAN/LIN) | Static matrix | Hard-RT control, ASIL-D actuation | Dynamic services, OTA-added APIs | Static schedule + bus-load analysis |
| Adaptive `ara::com` over SOME/IP | SOME/IP-SD multicast | Adaptive services, Classic↔Adaptive bridge | Large fan-out telemetry, sub-ms jitter | SOME/IP QoS + TSN class; explicit deadline |
| DDS (Fast/Cyclone) | RTPS discovery, rich QoS | Many-to-many perception/fusion | Constrained ECUs | QoS-driven; pairs with TSN + time-sync |
| Zenoh | Routable pub/sub + query | Zonal aggregation, edge↔cloud | Hard-RT closed loop | Characterize multi-hop latency |
| MQTT v5.0 | Brokered pub/sub | Telematics, off-board shadow | In-vehicle RT paths | Broker is SPOF; never on deadline path |
| Zero-copy IPC (iceoryx-style) | On-target | Same-SoC high-bandwidth chains | Cross-ECU services | Prove no-copy path in test |

Decision rules: hard deadlines (<10 ms, ASIL C–D) stay on Classic/MCU or RT partition;
one service = one binding; discovery scope bounded (VLAN + TTL + SD domain);
OTA-added services use versioning-tolerant bindings; containers must join gPTP domain.

## Rules — IDL, versioning, back-compat

1. One IDL source of truth per service (Franca/ARXML, OMG IDL, protobuf/JSON-Schema).
   Generated code records generator + version; hand-edited generated files fail review.
2. Semantic versioning `major.minor.patch` on every interface; gateways reject unknown
   major; tolerate unknown minor — tested, not assumed.
3. Back-compat suite mandatory: N-1/N matrices in CI; breaking changes need ADR + migration window.
4. Every vehicle-exposed signal maps to a COVESA VSS path/VSC entry or records explicit gap.
5. No silent truncation: conversions explicit, range-checked, logged; unknown enums → `UNKNOWN`.

## Rules — QoS and deadlines

1. Every service declares pattern, payload range, rate, deadline, reliability,
   durability/history, liveliness lease, priority/TSN class.
2. QoS table is normative (DDS XML, SOME/IP QoS, Zenoh settings versioned, hashed, reviewed).
3. Deadlines are end-to-end with middleware slice sub-budgets; a service without a
   deadline is best-effort and cannot feed a safety argument.
4. Backpressure policy declared per topic; unbounded queues forbidden.

## Rules — TSN, time-sync, scheduling

1. One gPTP domain (IEEE 802.1AS) per deterministic partition; max clock error declared + tested.
2. TSN class per stream: Qbv windows for scheduled traffic; Qav/CBS for reserved;
   best-effort preemptible. Configs versioned, validated against switch capability.
3. Converged-traffic guardrails: cloud/diagnostics traffic rate-limited, never shares
   Qbv window with control traffic.
4. OS isolation pairs with scheduling: PREEMPT_RT + isolcpus/cpusets; middleware thread
   priorities mapped from TSN classes; PI mutexes on deadline paths.

## Rules — security and observability

1. Per-binding security profile: SecOC/authenticated transport in-vehicle; DDS-Security
   plugins; mutual TLS 1.2+ for Zenoh/MQTT/SOME-IP cross-zone; keys in HSM/TrustZone.
2. Gateways enforce auth per service; discovery info filtered at zone boundaries.
3. Observability built in: per-service latency/jitter/loss/age histograms, discovery log,
   QoS-mismatch counters, time-sync health, trace IDs across hops.

## Integration and test strategy

1. Timing budgets per service: nominal/p99/max latency, jitter, loss, discovery-convergence,
   cold-start — measured on target under full load; host-only numbers labeled provisional.
2. Harness minimum: loopback, switched pair, full-topology rig (TSN + gPTP), containerized deployment.
3. Fault/chaos injection: killed broker/router/daemon, link flap, switch reboot, grandmaster
   loss, multicast storm, slow subscriber, clock jump, malformed payload, version-skew peers.
4. Interop: vsomeip↔`ara::com`, DDS vendor A↔B, Zenoh failover, VSS round-trip, MQTT bridge contract.
5. OTA-readiness: install N-1 → N with running services; discovery convergence, negotiation,
   rollback, power-loss survival.
6. Soak ≥24h on deterministic services with pcap + gPTP logs; any deadline miss is a defect.

## Traceability

- SYS-xxx → MW-xxx → `idl/` version → binding `config/` hash → `test/` → evidence id.
- Middleware configs hashed (vsomeip JSON, DDS XML, Zenoh, Qbv, gPTP); AUTOSAR items by
  document ID + release; DDS/TSN/VSS by spec + version + clause + URL.

## Compliance mapping (via overlays, not duplication)

- ISO 26262:2018 via `domains/automotive/`; ISO/SAE 21434 TARA → security profiles;
  UNECE R155/R156 for OTA-affected services. Never claim certification or type approval.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill automotive-middleware` → PASS.
2. Selection matrix per service with winner + rejected alternatives.
3. IDL pinned + generator recorded; N-1/N back-compat matrix green.
4. QoS + TSN/Qbv + gPTP configs versioned, hashed, reviewed; skew paths tested.
5. Timing budgets measured on target; soak + chaos green; VSS/VSC mapping complete.
6. Security profiles + observability demonstrated; deltas flagged for human review.

Load task-specific domain/platform/rule overlays before execution.
