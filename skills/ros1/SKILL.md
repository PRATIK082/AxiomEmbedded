---
name: ros1
description: 'ROS1 (Noetic) development: node/topic/launch design, TF, actionlib, nodelets, pitfalls, and ROS1-to-ROS2 migration. Use when maintaining or extending ROS1 systems.'
version: 1.0.0
domains: [all]
platforms: [linux, ros1]
axiom:
  dotted_name: axiom.legacy.ros1
  domain: all
  subdomain: legacy
  category: legacy
  maturity: beta
  owner: axiom-embedded
  tags:
  - legacy
  - ros
  - ros1
---

# ROS1 Development Skill

Production-grade ROS1 (Noetic) knowledge for AI coding assistants.

## When to Use
- Maintaining or extending existing ROS1 systems
- Writing new ROS1 nodes/packages
- Migrating ROS1 → ROS2
- Debugging ROS1 systems

## Core Architecture Principles

### 1. Node Design
- Decompose into single-purpose nodes (one responsibility each). Avoid monolithic nodes.
- Use nodelets for zero-copy in-process transport when latency matters.
- Namespace and remap topics via launch files, not hardcoded.

### 2. Topic Design
- Sensor data (high frequency, OK to drop old): `queue_size=1` to `5`, best-effort-ish.
- Commands (must not miss): `queue_size=10+`, reliable.
- Large data (point clouds, images): small queues to prevent memory bloat.
- **NEVER use `queue_size=0` (infinite) for high-frequency topics** — causes memory leaks under load.
- Robot description, static maps, calibration: `latch=True`, `queue_size=1`.

### 3. Launch File Best Practices
- Use `<include>` for composition and `<arg>` for parameterization.
- Use `<group ns="">` for namespacing.
- Set `respawn="true"` for critical nodes with `respawn_delay`.
- Use `<param>`/`<rosparam>` for config; avoid hardcoding.

### 4. TF Transform Tree
- Publish transforms with `tf2_ros.TransformBroadcaster` (or `tf.TransformBroadcaster` legacy).
- Listen with timeout and exception handling (`tf2_ros.LookupException`, `ConnectivityException`, `ExtrapolationException`).
- Maintain a single, consistent transform tree; avoid multiple publishers for the same frame.
- Use `static_transform_publisher` for fixed transforms.

### 5. Actionlib for Long-Running Tasks
- Use action servers for tasks with feedback and cancellation (navigation, manipulation).
- Implement goal preemption, cancellation, and result reporting.
- Use `SimpleActionServer` for simple cases, `ActionServer` for advanced.

## Common Pitfalls & Failure Modes

### Time Synchronization
- Don't compare timestamps from different clocks without sync.
- Use `message_filters` (ApproximateTimeSynchronizer) for multi-sensor fusion.
- Use `ros::Time::now()` consistently; handle simulated time (`use_sim_time`).

### Callback Threading
- ROS1 uses single-threaded spinner by default; long callbacks block all others.
- Use `MultiThreadedSpinner` or process in a separate thread.
- Protect shared state with mutexes.

### Parameter Server Anti-Patterns
- Don't hardcode values; use private params with defaults.
- Use dynamic reconfigure for runtime tuning.
- Namespace params per node (`~param`), not global.

### Nodelets for Zero-Copy Transport
- Use nodelets when multiple processing stages share large data (images, point clouds).
- Load via `nodelet load` in a manager; unload on shutdown.

## Package Structure
```
my_package/
├── CMakeLists.txt
├── package.xml
├── src/          (C++ nodes)
├── scripts/      (Python nodes)
├── launch/
├── config/
├── msg/ srv/ action/
└── tests/
```

## Debugging Toolkit
- Topic inspection: `rostopic list/echo/hz/bw/info`
- Node inspection: `rosnode list/info`
- TF debugging: `rosrun tf view_frames`, `rosrun tf tf_echo`
- Bag files: `rosbag record/play/info`
- Parameter: `rosparam list/get/set`

## ROS1 → ROS2 Migration Checklist
- [ ] Replace catkin with colcon/ament
- [ ] Replace rospy/roscpp with rclpy/rclcpp
- [ ] Replace launch XML with Python launch files
- [ ] Replace tf with tf2
- [ ] Replace actionlib with rclcpp_action / rclpy action
- [ ] Replace dynamic_reconfigure with ROS2 parameters
- [ ] Replace nodelets with components (composable nodes)
- [ ] Update QoS (ROS1 had implicit reliable; ROS2 requires explicit)
- [ ] Update message definitions (same .msg/.srv, but build system changes)
- [ ] Test with ros2 bag (different format from rosbag)
- [ ] Update CI/CD for ROS2

## Anti-Patterns
1. Monolithic node doing perception+planning+control.
2. `queue_size=0` (infinite) on high-frequency topics.
3. Blocking callbacks in single-threaded spinner.
4. Hardcoded parameters.
5. No TF exception handling.
6. No time synchronization for multi-sensor.
7. Running without bags/recording for debugging.

## Checklist
- [ ] Nodes are single-purpose
- [ ] Topics have appropriate queue_size and latch
- [ ] Launch files use args/includes, not hardcoded
- [ ] TF transforms published/listened with exception handling
- [ ] Actionlib used for long-running tasks
- [ ] Time synchronization handled (message_filters)
- [ ] Callback threading considered (multi-threaded spinner if needed)
- [ ] Parameters namespaced with defaults
- [ ] Bags recorded for debugging
- [ ] Migration path to ROS2 documented if applicable
