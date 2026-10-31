---
name: robotics
description: ROS 2 distro policy, interface-first nodes, real-time paths, simulation-first testing. Use when building robot behaviors on embedded compute.
version: 1.3.0
domains: [robotics, industrial]
platforms: [mpu, soc, linux]
axiom:
  dotted_name: axiom.legacy.robotics
  domain: robotics
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills:
  - axiom-robotics-system-integration
  checklists:
  - checklists/robotics-checklist.md
---

# Robotics skill

ROS 2-based robot software for embedded compute: node architecture, real-time
control paths, navigation and manipulation stacks, simulation-first testing,
and field lifecycle (logging, OTA, fleet monitoring) — grounded in the
current ROS 2 LTS landscape.

## 1. Purpose and scope

**Purpose.** Build robot behaviors that are deterministic where it matters
(control loops), observable everywhere (logging/bags), and testable without
hardware (simulation-first CI).

**In scope.** ROS 2 architecture (nodes, topics, services, actions, lifecycle),
DDS/Zenoh middleware configuration, real-time executors, Nav2 navigation,
MoveIt manipulation, Gazebo simulation, rosbag-based testing, launch testing,
and deployment on embedded Linux compute (see `embedded-linux`).

**Non-goals.** Mechanical design, low-level motor-driver firmware (see `mcu`,
`drivers`), and cloud fleet backends beyond the robot-side interface.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Scope | Source |
|---|----------|------------------|-------|--------|
| 1 | ROS 2 Kilted Kaiju | Released May 2025, current latest | New development baseline | `https://docs.ros.org/en/kilted/` |
| 2 | ROS 2 Jazzy Jalisco | LTS, supported to 2029 | Stable baseline for products started 2024–2025 | `https://docs.ros.org/en/jazzy/` |
| 3 | ROS 2 Humble Hawksbill | LTS, supported to 2027 | Maintenance baseline; migrate before EOL | `https://docs.ros.org/en/humble/` |
| 4 | DDS default / Zenoh option | RMW abstraction; Zenoh RMW available as alternative transport | Middleware selection per network topology | `https://docs.ros.org/en/kilted/Concepts/About-Transports.html` |
| 5 | Nav2 / MoveIt 2 | Current stacks on above distros | Navigation and manipulation frameworks | `https://navigation.ros.org/` |

> Distro rule. New products start on the newest supported distro (Kilted);
> existing products track their LTS to EOL with a migration trigger 12 months
> before end of support — same policy shape as `embedded-linux` §3.

## 3. Architecture — nodes, interfaces, lifecycle

1. **Interface-first.** Every topic/service/action message is defined in a
   dedicated interface package with versioning; nodes depend on interfaces,
   never on each other's internals. Breaking interface changes require a
   migration note (same contract rule as skill manifests).
2. **Lifecycle nodes for managed startup.** Sensors, drivers, and safety
   monitors use managed lifecycle states (`unconfigured → inactive → active`)
   so bring-up order is explicit and shutdown is orderly — no action at
   process start before the lifecycle transition.
3. **Deterministic control path.** Hard real-time loops run in an `rclcpp`
   real-time executor with pinned threads, or on an MCU/RTOS coprocessor with
   a narrow command/state interface (see `rtos` §5). No memory allocation,
   logging, or parameter callbacks in the control callback.
4. **Middleware tuning.** DDS profile (reliability, durability, history depth,
   deadlines) is specified per topic from its timing requirement; default QoS
   everywhere is a review finding. Zenoh RMW is preferred for constrained or
   lossy robot-to-robot links — decision recorded with measured rationale.

## 4. Navigation, manipulation, perception

1. **Nav2.** Behavior trees compose planners, controllers, and recoveries;
   costmap sources, footprint, and controller rates are versioned parameters
   with recorded tuning sessions (rosbags kept as evidence).
2. **MoveIt 2.** Planning scene, kinematics plugins, and collision matrices
   are configuration artifacts under review; every motion plan executes
   through trajectory validation (limits, collisions, singularities) before
   hardware.
3. **Perception/ML.** Vision or lidar-ML nodes follow the `edge-ai` deployment
   pipeline; perception outputs carry confidence and timestamp validity, and
   safety-relevant perception routes to `ai-validation`.

## 5. Simulation-first testing

1. **Gazebo before hardware.** Every behavior has a Gazebo scenario exercising
   nominal, degraded (sensor dropout), and adversarial (dynamic obstacles)
   cases; CI runs the simulation suite on every change.
2. **Bag-driven regression.** Recorded rosbags (sensor data + ground truth)
   replay through perception and planning nodes in CI with metric thresholds
   (success rate, path deviation, planning latency) — metric regressions block.
3. **Launch testing.** `launch_testing` covers multi-node bring-up, lifecycle
   transitions, fault injection (node death, topic stall), and parameter
   validation.

## 6. Release gates (blocking)

1. Distro pinned and supported; EOL trigger recorded.
2. Interface packages versioned; no cross-node private dependencies.
3. Control-path determinism measured (jitter/latency) or delegated to RTOS/MCU.
4. Simulation suite green: nominal + degraded + adversarial scenarios.
5. Bag-regression metrics within thresholds; no unreviewed metric relaxation.
6. Safety-relevant functions traced per `safety` §4 with independent assessment
   where the integrity level demands it.

## 7. Verification of this skill (Phase 4 gate)

- Distro claims carry version + support window + URL (§2).
- Default-QoS-everywhere and hardware-only testing both fail review (§3.4, §5).



## 7. Robotics software design principles (production-grade)

### 7.1 Why robotics software is different
Robotics software must handle real-time constraints, safety, hardware variability, and failure modes not present in typical software. AI assistants must design for bounded execution, safe defaults, and graceful degradation.

### 7.2 Core principles
1. **Single Responsibility** â€” one module, one job. No god modules mixing perception+planning+control+logging. Separate into perception_node, planner_node, controller_node, logger_node with clear interfaces.
2. **Dependency Inversion** â€” depend on abstractions, not hardware. Define contracts (sensor_if, actuator_if) in abstract base classes; concrete implementations (RealSenseCamera, MockCamera) implement them; high-level code depends only on abstractions.
3. **Open-Closed** â€” extend without modifying. Plugin architecture: core pipeline never changes when adding sensors; add a file + register at startup.
4. **Interface Segregation** â€” small, focused interfaces. Don't force every camera to implement RGB+Depth+PTZ; segregate into RGBProvider, DepthProvider, PTZController.
5. **Liskov Substitution** â€” replaceable implementations. Self-describing implementations (joint count from config, not hardcoded); caller code generic, works with any arm.
6. **Separation of Rates** â€” respect timing boundaries. Decouple perception (30Hz) from control (1000Hz) via async boundaries; perception must not block control loop.
7. **Fail-Safe Defaults** â€” safe until proven otherwise. Default to stopped, zero velocity, brakes engaged; must explicitly opt into danger.
8. **Configuration Over Code** â€” externalize everything that changes. No hardcoded thresholds; use YAML config files (approach_height_m, grasp_force_n, etc.).
9. **Idempotent Operations** â€” safe to retry. Sending same command twice has same effect as once; use state-based not delta-based commands.
10. **Observe Everything** â€” you can't debug what you can't see. Metrics, structured logging, health checks, tracing.
11. **Composability** â€” build complex behaviors from simple ones. Primitive skills (move_to, grasp) composed into composite skills (pick_and_place) via dependency injection.
12. **Graceful Degradation** â€” work with what you have. If LiDAR fails, fall back to camera+IMU; if camera fails, use LiDAR only.

### 7.3 Quick reference checklist
- [ ] Each module has single responsibility
- [ ] High-level code depends on abstractions, not hardware
- [ ] New sensors/actuators added without modifying core
- [ ] Interfaces are small and focused
- [ ] Implementations are substitutable
- [ ] Perception/control rates decoupled
- [ ] Defaults are safe (stopped, zero velocity)
- [ ] Thresholds in config files, not code
- [ ] Commands are idempotent
- [ ] Metrics and structured logging present
- [ ] Behaviors composed from primitives
- [ ] System degrades gracefully on component failure

## 8. Robotics design patterns

### 8.1 The robot software stack
Layered: Hardware â†’ Drivers â†’ Perception â†’ Planning â†’ Control â†’ Application, with clear interfaces between layers.

### 8.2 Behavior Trees (BT)
Core node types: Sequence, Fallback (Selector), Parallel, Decorator, Action, Condition. Use for task-level decision making. Blackboard for shared state: perception nodes WRITE, action nodes READ.

### 8.3 Finite State Machines (FSM)
Use for simple, well-defined state transitions (SMACH or custom). Define states, transitions, guards. Prefer BT for complex/long-running tasks; FSM for simple sequences.

### 8.4 Perception pipeline
Sensor fusion architecture: raw sensor â†’ preprocessing â†’ feature extraction â†’ fusion â†’ world model. Perception-action loop timing: perception must not block control; use async boundaries and bounded queues.

### 8.5 Hardware Abstraction Layer (HAL)
Factory pattern for hardware instantiation. Abstract sensor/actuator interfaces; concrete implementations selectable via config. Enables sim-to-real switching.

### 8.6 Safety systems
Safety hierarchy: E-stop (hardware) â†’ Safety controller (isolated) â†’ Software watchdog â†’ Application. Software watchdog pattern: periodic heartbeat; if missed, trigger safe state. Workspace limits: enforce joint/velocity/position bounds in software as backup to hardware limits.

### 8.7 Sim-to-real architecture
Config-driven sim/real switching: same code, different backend (Gazebo/Isaac Sim vs real hardware) selected via launch param. Avoid sim-only code paths; test in sim then validate on hardware.

### 8.8 Data recording architecture
Record sensor data, commands, state for replay and debugging. Use rosbag2 or custom recorders. Include timestamps, frame IDs, calibration version.

### 8.9 Anti-patterns to avoid
1. **God Node** â€” one node doing everything; split by responsibility.
2. **Hardcoded Magic Numbers** â€” use config files and named constants.
3. **Polling Instead of Events** â€” use callbacks/subscriptions, not spin loops.
4. **No Error Recovery** â€” handle sensor failures, comm drops, actuator faults.
5. **Sim-Only Code** â€” code that only works in simulation; must run on real hardware.
6. **No Timestamps** â€” every message needs a header with stamp and frame_id.
7. **Blocking the Control Loop** â€” perception/logging must not block real-time control.
8. **No Data Logging** â€” always record for debugging; production robots need audit trails.

### 8.10 Architecture decision checklist
- [ ] Node responsibilities are single-purpose
- [ ] Interfaces are abstract and substitutable
- [ ] Safety hierarchy is implemented (E-stop â†’ safety controller â†’ watchdog â†’ app)
- [ ] Sim and real use same code path (config-driven)
- [ ] All messages carry timestamps and frame IDs
- [ ] Control loop is never blocked by non-real-time work
- [ ] Data recording is enabled for debugging
- [ ] Error recovery is implemented for sensor/actuator failures
- [ ] Configuration is externalized (no hardcoded values)
- [ ] Observability (metrics, logs, health) is present




## 7. Robotics security (production-grade)

### 7.1 The robot attack surface
Network (DDS/ROS2 topics), physical (USB, serial), software (deps, containers), supply chain. Robots are cyber-physical: security failures can cause physical harm.

### 7.2 SROS2: DDS security
Generate per-node enclaves with certificates (sros2 create_keystore, create_enclave). Sign governance and permissions XML. Enable security in launch files (RMW_QOS... env, security env vars). Per-topic access control (allow/deny publish/subscribe per node).

### 7.3 Network hardening
Network segmentation: VLANs for control/data/management. Firewall rules for DDS (SPDP discovery ports, SEDP data ports). Disable DDS multicast in production (unicast peers). ROS_DOMAIN_ID isolation per robot.

### 7.4 SSH and host hardening
SSH key-only auth, disable root login. fail2ban. Unattended security updates (never auto-reboot). Minimal installed packages. Per-robot SSH keys (not shared across fleet).

### 7.5 Secrets management
No hardcoded credentials in code or params.yaml. Use environment variables / systemd EnvironmentFile with locked permissions (chmod 600). Certificate rotation via cron. File permissions: CA private key root-only.

### 7.6 Container security
Non-root containers (USER robot). Minimal runtime images (remove shell/package manager). Image scanning and signing. Read-only root filesystem with overlay.

### 7.7 Physical-cyber safety intersection
E-stop independence (hardware, not software-only). Safety controller isolation (separate process/computer). Command velocity validation and rate limiting (safety gate node). Watchdog independence (hardware watchdog reboots if software unresponsive).

### 7.8 Secure boot and firmware
Read-only root filesystem with overlay (writes lost on reboot). Signed container images. TPM-based disk encryption (LUKS+TPM2). Firmware update verification (signed updates).

### 7.9 Audit and monitoring
Security logging for ROS2 (topic auditor logs publications on sensitive topics). Intrusion detection on command topics (cmd_vel anomaly detector). auditd rules for robot systems. Monitor for unauthorized publishes.

### 7.10 Robotics security anti-patterns
1. Unauthenticated /cmd_vel (anyone on network can control robot).
2. Shared SSH keys across fleet.
3. Running all nodes as root.
4. No network segmentation.
5. Hardcoded credentials in launch files.
6. E-stop over network (sole e-stop is a ROS2 topic subscriber).
7. No certificate rotation.
8. Disabling security for convenience ("temporary" becomes permanent).

### 7.11 Robotics security checklist
- [ ] SROS2 enabled with per-node enclaves
- [ ] DDS security policies (governance + permissions) signed
- [ ] Network segmented (VLANs) and firewalled
- [ ] SSH key-only, no root login, fail2ban
- [ ] Secrets in EnvironmentFile (chmod 600), not git
- [ ] Containers run as non-root, minimal images, scanned
- [ ] E-stop is hardware-independent
- [ ] Safety controller isolated from application
- [ ] Command velocity validated and rate-limited
- [ ] Hardware watchdog enabled
- [ ] Secure boot / signed updates where applicable
- [ ] Security logging and intrusion detection active
- [ ] Certificate rotation automated

