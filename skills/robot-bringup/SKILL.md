---
name: robot-bringup
description: 'ROS2 system bringup: systemd services, launch composition, udev rules, network/DDS config, watchdogs, logging, graceful shutdown, remote monitoring. Use when deploying or operating robots in production.'
version: 1.0.0
domains: [all]
platforms: [linux, ros2]
axiom:
  dotted_name: axiom.legacy.robot-bringup
  domain: all
  subdomain: legacy
  category: legacy
  maturity: beta
  owner: axiom-embedded
  tags:
  - robotics
  - ros2
  - bringup
  - deployment
---

# Robot Bringup Skill

Production-grade ROS2 system bringup and deployment for AI coding assistants.

## When to Use
- Deploying robots to production
- Setting up systemd services for ROS2 stacks
- Configuring udev rules for deterministic device names
- Network/DDS configuration for multi-machine setups
- Watchdog and heartbeat monitoring
- Logging and log rotation
- Graceful shutdown sequences
- Remote monitoring and debugging

## The Robot Bringup Stack
Hardware → Drivers → Perception → Application, each as a systemd service with explicit dependencies.

## systemd Service Units for ROS2
- Basic unit: EnvironmentFile for ROS env, pre-start device check, ExecStart sourcing setup.bash, SIGINT for graceful shutdown, Restart=on-failure with rate limits.
- Environment file: ROS_DISTRO, RMW_IMPLEMENTATION, ROS_DOMAIN_ID, CYCLONEDDS_URI, robot config.
- Service dependencies: drivers → perception → application via After=/Requires=.
- Restart policies: Restart=on-failure, StartLimitBurst, StartLimitIntervalSec, RestartSec ramp-up.
- Resource limits: MemoryMax, CPUQuota, rtprio for real-time drivers, ProtectSystem/ProtectHome.
- Watchdog: WatchdogSec triggers restart; hardware watchdog reboots if systemd unresponsive.

## Launch File Composition and Layering
- Hardware layer: device drivers, sensor nodes.
- Driver layer: hardware interfaces, calibration.
- Perception layer: cameras, LiDAR, detection, tracking.
- Application layer: planning, control, behavior.
- Top-level bringup: includes all layers with conditionals (sim vs real, robot variants).

## Ordered Startup with Health Checks
- Startup dependency graph: hardware → drivers → perception → application.
- Health check scripts: verify devices present, wait for nodes/topics.
- Lifecycle node orchestration: configure → activate in order.
- Wait-for-topic pattern for synchronization.

## udev Rules for Deterministic Device Naming
- Cameras by USB port path or serial number.
- Serial devices (IMU, motor controller, GPS, LiDAR) by serial/port path.
- Reload with `udevadm control --reload-rules && udevadm trigger`.
- Test with `udevadm test`.

## Network Configuration for Multi-Machine ROS2
- Static IP via netplan.
- DDS discovery: CycloneDDS unicast peers or FastDDS.
- Firewall: open SPDP discovery + SEDP data ports; or allow robot subnet.
- ROS_DOMAIN_ID isolation per robot; ROS_LOCALHOST_ONLY=0 for multi-machine.

## Watchdog and Heartbeat Monitoring
- systemd watchdog: sd_notify(WATCHDOG=1) within WatchdogSec.
- ROS2 heartbeat monitor: monitor critical nodes, trigger safe stop on silence.
- Hardware watchdog: RuntimeWatchdogSec in systemd; reboots if unresponsive.
- Check: `systemctl show <unit> -p WatchdogUSec`.

## Logging and Log Rotation
- ROS2 log levels via env/params/runtime.
- journald: persist logs, SystemMaxUse, rate limiting, export.
- logrotate for ROS2 log files.
- Structured logging for production (event + fields).

## Graceful Shutdown Sequences
- Signal handling: SIGINT (ROS2 handler) → safe state → cleanup → exit.
- Ordered shutdown via systemd Before=/After= (reverse of start).
- Safe state on shutdown: stop motion, hold position, log.

## Remote Monitoring and Debugging
- SSH tunneling for DDS traffic.
- Remote journalctl and service management.
- Deploy updates via SSH (build locally, copy, restart).
- Stream structured logs as JSON.

## Anti-Patterns
1. Sourcing setup.bash in .bashrc for systemd (use EnvironmentFile + explicit source).
2. No startup ordering (parallel start with no dependencies).
3. Restart=always without rate limiting (infinite restart loop).
4. network.target instead of network-online.target.
5. No log rotation (disk fills).
6. Hardcoded device paths (/dev/ttyUSB0) — use udev symlinks.
7. Running entire stack as root — use dedicated user.
8. No graceful shutdown handler.

## Bringup Checklist
- [ ] systemd units with EnvironmentFile and explicit sourcing
- [ ] Service dependencies ordered (hardware→drivers→perception→app)
- [ ] Restart policies rate-limited with failure notification
- [ ] udev rules for deterministic device names
- [ ] Network configured (static IP, DDS discovery, firewall)
- [ ] Watchdog enabled (systemd + hardware)
- [ ] Logging configured (journald + logrotate)
- [ ] Graceful shutdown handlers implemented
- [ ] Resource limits set (memory, CPU, rtprio)
- [ ] Remote monitoring and deploy scripts tested
- [ ] Launch files layered and parameterized
- [ ] Health checks before service start
- [ ] Tested reboot recovery (power cycle)
