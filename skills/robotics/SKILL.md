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
