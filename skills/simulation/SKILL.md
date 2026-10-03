---
name: simulation
description: MIL-SIL-HIL progression, back-to-back evidence, scenario discipline. Use when testing without hardware or qualifying models.
version: 1.2.0
domains: [all]
platforms: [all]
---

# Simulation skill

Modeling and simulation across the V-model: MIL/SIL/HIL progression,
plant and environment models, simulator qualification for credit, and the
scenario discipline that makes simulation evidence trustworthy.

## 1. Purpose and scope

**Purpose.** Verify behavior cheaply (MIL/SIL) and credibly (HIL) before and
alongside hardware, with known model fidelity bounds so simulation results
transfer to reality.

**In scope.** Plant/environment modeling, MIL→SIL→HIL progression, real-time
simulation platforms, scenario design (nominal/degraded/adversarial),
model validation against measurements, simulator qualification where results
take verification credit, and co-simulation interfaces (FMI).

**Non-goals.** Hardware design and production testing. Ends at simulation
results with quantified fidelity attached — never bare pass/fail.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | FMI (Functional Mock-up Interface) | 3.0 (2022, Modelica Association) | Co-simulation and model-exchange interface standard | `https://fmi-standard.org/` |
| 2 | ISO 26262-6 Software level | 2018 | Clause 9: back-to-back comparison between SIL/HIL and target for verification credit | `https://www.iso.org/standard/68389.html` |
| 3 | DO-331 Model-based supplement to DO-178C | 2011 | Model coverage, simulation-case verification for airborne credit | `https://www.rtca.org/products/model-based-development-and-verification-supplement-to-do-178c-and-do-278a-do-331/` |
| 4 | Gazebo robotics simulator | Current (Gazebo Sim / Harmonic+ collections) | Physics-based robot/environment simulation | `https://gazebosim.org/` |

## 3. Progression rules

1. **MIL → SIL → HIL in order.** Algorithms against plant models (MIL),
   production code against simulated plant (SIL), production code on target
   ECU against real-time plant (HIL). Skipping levels requires rationale; each
   level's discrepancies are tracked, not normalized away.
2. **Back-to-back comparison.** SIL-vs-target and HIL-vs-vehicle comparisons
   quantify the transfer gap; results that take verification credit need the
   comparison evidence (26262-6 §9, DO-331).
3. **Real-time honesty.** HIL plant models run in hard real time with measured
   step overruns reported; overrunning steps invalidate the run segment they
   corrupt — silently kept overruns are data fabrication.
4. **Scenario coverage.** Nominal, degraded (sensor dropout, actuator limits),
   and adversarial (fault injection per `fault-injection`, edge cases per ODD
   in `ai-validation`) scenarios versioned with the models that ran them.

## 4. Model credibility

Plant models carry fidelity bounds validated against measurements (frequency
response, step response, parameter tolerances); using a model outside its
validated envelope voids the results. Model, parameter set, simulator version,
and scenario IDs are recorded with every result — unreproducible simulation
is not evidence.

## 5. Release gates (blocking)

1. MIL/SIL/HIL results present at the required progression with discrepancy logs.
2. Back-to-back evidence where credit is claimed.
3. Scenario suite covers nominal + degraded + adversarial; models within
   validated envelopes.

## 6. Verification of this skill (Phase 4 gate)

- Standards cited with number + version + clause + URL (§2).
