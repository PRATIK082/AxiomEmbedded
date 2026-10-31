---
name: axiom-adas-perception-pipeline
title: ADAS Perception Pipeline Design
description: >
  Designs sensor-abstraction, perception interfaces and object-model contracts for ADAS pipelines.
version: 1.3.0
author: PRATIK PATIL
license: Apache-2.0
domains: [automotive]
platforms: [mpu, soc]
axiom:
  dotted_name: axiom.automotive.adas.perception.pipeline
  domain: automotive
  subdomain: adas
  category: design
  maturity: experimental
  owner: axiom-embedded
  tags: [adas]
  related_skills: []
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: [ISO 26262:2018]
  artifact_types: [perception interface contract]
  mcp_tools: [run_skill, validate_skill]
  risk_level: high
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom ADAS Perception Pipeline Design

## Purpose
Designs sensor-abstraction, perception interfaces and object-model contracts for ADAS pipelines.

Scope: adas (automotive). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the adas perception pipeline design engineering workflow.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Domain artifacts for adas (see skill references/).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing adas artifacts.
3. Select method/template from this skill.
4. Generate or modify artifacts (dry-run first).
5. Validate structurally and semantically (scripts/ + checklists/).
6. Run applicable checks; record results.
7. Produce traceability and review evidence.
8. Summarize assumptions, risks, next actions.

## Tool Invocations
- `run_skill` with structured context; dry-run before writes.
- `validate_skill` must pass before release use.
- MCP tools: run_skill, validate_skill.

## Decision Rules
- Prefer explicit configuration over invented defaults; flag every assumption.
- Safety/security-relevant outputs require human review (review_required: true).

## Workflow
Follow Execution Workflow; record per-step evidence in the run manifest.

## Deliverables
- Run report under `.axiom/runs/<timestamp>/axiom-adas-perception-pipeline/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-adas-perception-pipeline`.
2. Review checklist gates.
3. Human review for high/safety-critical risk levels.

## Common Failure Modes
- Missing inputs invented instead of flagged -> require explicit inputs.
- Unreviewed safety/security output merged -> block at review gate.

## Guardrails
- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.
- Never claim certification or compliance from heuristic checks.

## References
- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.



## 7. Robot perception (production-grade)

### 7.1 Sensor landscape
Sensor types: cameras (RGB/depth/stereo), LiDAR (2D/3D), IMU, radar, ultrasonic, force/torque. Characteristics: framerate, latency, accuracy, field of view, range, environmental robustness. Common hardware: RealSense, OAK-D, Velodyne, Ouster, ZED, Kinect.

### 7.2 Camera models and calibration
Pinhole camera model: intrinsics (fx, fy, cx, cy), distortion (k1,k2,p1,p2,k3). Intrinsic calibration via checkerboard/charuco. Extrinsic calibration (camera-to-camera, camera-to-LiDAR). Hand-eye calibration (camera-to-robot). Validate calibration quality (reprojection error < 0.5px).

### 7.3 Sensor streaming best practices
- Decouple capture from processing (separate threads, bounded queues).
- Bounded buffers with drop policy (never unbounded).
- Timestamp at capture time, not processing time.
- Event-driven or spin with wall clock (not sleep-based timing).
- Multi-sensor synchronization: hardware trigger or software sync (message_filters approximate time).
- Streaming anti-patterns: capture+process in same thread, unbounded buffer, sleep for timing, timestamp at processing time.

### 7.4 RGB processing pipelines
Image undistortion, object detection integration (YOLO/RT-DETR), fiducial marker detection (AprilTag/ArUco), semantic segmentation for manipulation.

### 7.5 Depth processing
Depth map filtering (bilateral, hole filling), depth-to-point-cloud conversion, RGBD alignment (extrinsic calibration).

### 7.6 Point cloud processing
Filtering (voxel grid downsampling, statistical outlier removal), ICP registration, normal estimation.

### 7.7 Multi-sensor fusion
Perception fusion architecture: sensor nodes â†’ fusion node â†’ world model. Camera+LiDAR fusion (projection, association). Multi-object tracking (Kalman/JPDA).

### 7.8 Perception latency budget
Budget end-to-end: capture â†’ transfer â†’ preprocess â†’ inference â†’ postprocess â†’ publish. Target < 100ms for reactive control. Monitor and alert on budget exceeded.

### 7.9 Perception anti-patterns
1. Processing every frame when not needed (decimate).
2. Not validating depth values (check range, NaN, inf).
3. Assuming cameras are calibrated (load actual calibration).
4. Ignoring sensor warmup (discard initial frames).
5. Single-pixel depth sampling (use neighborhood median).
6. Not handling coordinate frame transforms (explicit frame tracking with tf2).

### 7.10 Production perception checklist
- [ ] Sensor drivers publish with correct QoS and timestamps
- [ ] Calibration loaded and validated (reprojection error)
- [ ] Capture decoupled from processing (bounded queues)
- [ ] Depth values validated before use
- [ ] Coordinate frames tracked explicitly (tf2)
- [ ] Sensor warmup handled
- [ ] Latency budget monitored
- [ ] Degradation on sensor failure (fallback)
- [ ] Multi-sensor fusion tested
- [ ] Perception outputs validated against ground truth

