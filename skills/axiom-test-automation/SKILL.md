---
name: axiom-test-automation
title: Embedded Test Automation
description: >
  Designs unit/integration test strategy, automation hooks and coverage expectations for embedded repos.
version: 1.3.0
author: PRATIK PATIL
license: Apache-2.0
domains: [all]
platforms: [mcu, mpu]
axiom:
  dotted_name: axiom.platform.test.automation
  domain: platform
  subdomain: testing
  category: verification
  maturity: experimental
  owner: axiom-embedded
  tags: [testing]
  related_skills: []
  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]
  standards: []
  artifact_types: [test strategy, test plan]
  mcp_tools: [run_skill, validate_skill]
  risk_level: low
  review_required: true
  safety_critical: false
  inputs: [repository path, target files, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: [validate_skill]
  optional_tools: [run_skill]
---

# Axiom Embedded Test Automation

## Purpose
Designs unit/integration test strategy, automation hooks and coverage expectations for embedded repos.

Scope: testing (platform). Maturity: experimental. This skill is original AxiomEmbedded content.

## When to Use
- The project needs the embedded test automation engineering workflow.
- Inputs listed below are available.

## When Not to Use
- As a substitute for qualified safety/security certification review.
- When the required inputs are absent (record the gap instead of inventing data).

## Required Inputs
- Repository path and target file list.
- User objective and constraints.
- Domain artifacts for testing (see skill references/).

## Optional Inputs
- Existing reports, prior run manifests, tool availability notes.

## Prerequisites
- `axiom doctor --skip-tests` green; relevant base skills loaded.

## Execution Workflow
1. Normalize the request into objective, scope, and constraints.
2. Inspect repo context and existing testing artifacts.
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
- Run report under `.axiom/runs/<timestamp>/axiom-test-automation/`.
- Skill-specific artifacts listed in catalog outputs.

## Acceptance Criteria
- `validate_skill` passes; checklist gates all green; traceability complete.

## Acceptance
- All checklist gates pass; findings carry severity + evidence + action.

## Validation Procedure
1. `python scripts/validate_skills.py --skill axiom-test-automation`.
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



## 7. Robotics testing (production-grade)

### 7.1 The robotics testing pyramid
Unit tests (pure functions, no ROS) â†’ component tests (ROS nodes in isolation) â†’ integration tests (launch files, multi-node) â†’ simulation tests (Gazebo/Isaac) â†’ hardware-in-the-loop tests â†’ field acceptance.

### 7.2 Unit testing ROS2 nodes with pytest
Use rclpy test fixtures, launch a node in-process, publish/subscribe, assert on outputs. Test pure functions (kinematics, filtering) without ROS dependency.

### 7.3 Property-based testing with Hypothesis
Generate random inputs for kinematics, transforms, filters; check invariants (orthonormality, range, monotonicity).

### 7.4 Integration testing with launch_testing
Launch a full system, wait for nodes/topics, run assertions, tear down. Use `launch_testing` with `@pytest.mark.launch_test`.

### 7.5 Mock hardware patterns
Abstract hardware behind interfaces; inject mocks for unit testing. Mock sensors publish synthetic data; mock actuators record commands.

### 7.6 Golden file testing (trajectory regression)
Record expected trajectories/outputs; compare new runs against golden files with tolerance. Detect regressions in planning/control.

### 7.7 Simulation testing
Run in Gazebo/Isaac Sim; test perception, planning, control in realistic physics. Use for regression and edge cases.

### 7.8 CI/CD pipeline for robotics
GitHub Actions: build matrix across ROS distros, run colcon test, launch_testing, lint (ament_lint), code coverage. Cache dependencies. Fail on warnings.

### 7.9 Testing anti-patterns
1. Testing with `sleep()` â€” use event-driven waiting with timeout.
2. Only testing happy path â€” test failures explicitly (sensor dropout, comm loss).
3. Non-deterministic tests â€” fix random seeds, use deterministic simulation.
4. No mock hardware â€” tests require real robot; use mocks.
5. No golden files â€” regressions undetected.
6. No CI â€” manual testing only.

### 7.10 Testing checklist
- [ ] Pure functions unit-tested (no ROS dependency)
- [ ] ROS nodes tested with pytest + launch_testing
- [ ] Mock hardware used for unit/integration tests
- [ ] Golden files for trajectory regression
- [ ] Simulation tests for perception/planning/control
- [ ] CI/CD runs tests on every PR
- [ ] Failure cases explicitly tested
- [ ] Tests are deterministic (fixed seeds)
- [ ] Coverage tracked and reported

