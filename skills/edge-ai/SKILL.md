---
name: edge-ai
description: >
  Model quantization, runtime/delegate selection, memory/latency/power budgets.
  Use when deploying ML inference on constrained targets.
version: 1.2.0
domains: [generic-embedded, automotive, industrial, iot, robotics]
platforms: [mcu, mpu, soc, mpsoc]

axiom:
  dotted_name: axiom.legacy.edge-ai
  domain: generic-embedded
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags: [legacy]

  related_skills: []
  checklists: [checklists/edge-ai-checklist.md]

  lifecycle: [discover, plan, implement, verify, evidence]
  standards: []
  artifact_types: [report, manifest]
  mcp_tools: []

  risk_level: medium
  review_required: true
  safety_critical: false
  inputs: [repository path, objective, constraints]
  outputs: [run report, run manifest]
  required_tools: []
  optional_tools: []
---
# Edge-AI skill

Deploying machine-learning inference on resource-constrained targets: model
selection and compression, framework and accelerator integration, memory and
latency budgeting, on-device evaluation, and lifecycle monitoring -- with
safety-relevant deployments routed through `safety` and `ai-validation`.

## 1. Purpose and scope

**Purpose.** Ship ML features (classification, detection, keyword spotting,
anomaly detection, sensor fusion) that meet accuracy, latency, memory, and
power budgets on MCU/MPU/SoC targets with a documented evaluation story.

**In scope.** Model optimization (quantization, pruning, distillation),
embedded inference frameworks, NPU/DSP/GPU delegate integration, arena and
bandwidth budgeting, on-device accuracy/latency/power measurement, dataset and
drift management, OTA model update.

**Non-goals.** Cloud training pipelines and foundation-model development. This
skill starts at an exported model artifact and ends at verified on-device
inference. Safety assurance of ML-based functions belongs to `ai-validation`
with the `safety` lifecycle; this skill provides the deployment engineering.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | MLPerf Tiny | v1.x inference benchmark suite for ultra-low-power devices | Latency/energy measurement methodology (anomaly detection, image classification, keyword spotting, visual wake words) | `https://mlcommons.org/benchmarks/mlperf-tiny/` |
| 2 | ONNX | Open format, opset-versioned | Portable model interchange between training and embedded runtimes | `https://onnx.ai/` |
| 3 | TensorFlow Lite for Microcontrollers | Current (TFLM, incl. Ethos-U delegate path) | MCU-class inference runtime, arena-based allocation | `https://www.tensorflow.org/lite/microcontrollers` |
| 4 | ExecuTorch | Current (PyTorch-native on-device runtime) | MPU/SoC-class deployment with delegate backends | `https://pytorch.org/executorch/` |

## 3. Model optimization pipeline

1. **Start from accuracy headroom.** Train or select with a 2-5 point accuracy
   margin above the product requirement; quantization and pruning spend that
   margin. No margin, no compression without a requirement waiver.
2. **Quantize deliberately.** Post-training INT8 quantization first; fall back
   to quantization-aware training when PTQ accuracy loss exceeds budget.
   Record per-tensor dynamic range and the calibration dataset ID -- the
   calibration set is a controlled artifact under `ai-validation` dataset rules.
3. **Prune and distill when needed.** Structured pruning for NPU/DSP targets
   (unstructured sparsity rarely accelerates on embedded cores); distillation
   to shrink architecture families for MCU flash limits.
4. **Verify numerics on target.** Accuracy is measured with on-device fixed-point
   inference, never with host-float simulation alone. Report accuracy delta
   (host float vs on-device quantized) per release.

## 4. Runtime selection and accelerator integration

| Target class | First-choice runtime | Delegate / accelerator path |
|--------------|---------------------|------------------------------|
| Cortex-M / low-end (KBs of RAM) | TFLM, static arena | CMSIS-NN kernels; Ethos-U NPU via delegate |
| Cortex-A / MPU (MBs) | ONNX Runtime Mobile, ExecuTorch | GPU/DSP/NPU delegates, FP16 where supported |
| SoC/MPSoC with vendor NPU | Vendor SDK via ONNX import | Quantization spec of the NPU toolchain is binding |

**Rules.** The delegate's supported-op list gates model design: unsupported ops
fall back to CPU and silently destroy latency budgets, so the op audit (S6.1)
runs before any latency claim. Vendor toolchains are pinned like Yocto layers
(see `embedded-linux` S3).

## 5. Budgeting -- memory, latency, power

1. **Memory.** Static arena sized from the runtime's recording allocator plus
   headroom; model flash + arena + input buffers + working scratch must fit
   with margin documented against the linker map. No heap growth at inference
   time.
2. **Latency.** Worst-case measured on target at worst-case clock/thermal
   corner, under full system load. Report p99/p100, not the mean -- control
   loops consume the tail.
3. **Power.** Energy per inference at the target duty cycle; NPU offload that
   halves latency but triples energy needs a system-level trade decision with
   the power budget owner.
4. **Bandwidth.** Feature-extraction and I/O transfer costs (camera, microphone,
   DMA) are part of the latency budget, not overhead discovered at integration.

## 6. Release gates (blocking)

1. Op audit: every model op supported on the chosen delegate path, or CPU
   fallback latency measured and budgeted.
2. On-device accuracy within the requirement with the quantized artifact;
   accuracy delta vs host float recorded.
3. p100 latency within budget at worst-case corner under full system load.
4. Static memory fit proven against the linker map; no dynamic allocation in
   the inference path.
5. Energy per inference within the power budget at the product duty cycle.
6. Calibration and evaluation dataset IDs recorded; drift-monitoring hooks (see
   `ai-validation`) wired for field data.

## 7. Verification of this skill (Phase 4 gate)

- Benchmark claims reference MLPerf Tiny methodology or a documented
  equivalent (S2.1), never ad-hoc host timings.
- Safety-relevant ML routes to `ai-validation` + `safety`; this skill alone
  never substantiates a safety claim.

## Copyright-safe standards references

No normative text from any standard is reproduced here. Only rule identifiers,
clause numbers, applicability metadata, and project-authored interpretations
are stored; verification is against the cited edition.

### Rule ID -> clause map

| Rule ID | Standard / clause | Impact tier |
|---|---|---|
| nist-ai-rmf-governance | NIST AI RMF 1.0 (govern/map/measure/manage) | MEDIUM |
| safety-ml-safety-case | Safety case for ML components | HIGH |
| security-model-integrity | Model integrity / secure update | MEDIUM |
| realtime-inference-latency | Inference latency budget | MEDIUM |
| data-privacy-pii-handling | GDPR / data minimization | LOW |

## Impact tiers

| Impact tier | Meaning | Typical handling |
|---|---|---|
| CRITICAL | Safety/security-critical; release blocker; core/evidence zone | Human approval required; no autonomous AI action |
| HIGH | Major correctness or compliance impact | Reviewed change; evidence required |
| MEDIUM | Moderate impact | Standard review |
| LOW | Minor or advisory | Batched review acceptable |

### Rule impact assignments

| Rule ID | Impact tier |
|---|---|
| nist-ai-rmf-governance | MEDIUM |
| safety-ml-safety-case | HIGH |
| security-model-integrity | MEDIUM |
| realtime-inference-latency | MEDIUM |
| data-privacy-pii-handling | LOW |

## Deviation management

Any deviation from a rule or standard in this skill must be recorded as a
first-class artifact (not a code comment) with all of the following:

- Rule ID
- Reason
- File / location
- Approver
- Date

Deviations against CRITICAL rules require a safety/security lead approval and
an impact assessment. Store deviation records under the project evidence or
change-control location and link them in the traceability matrix.

## Builder + reviewer pairing

This skill produces reviewable artifacts. Its outputs must be
independently checked by a human reviewer or the domain review skill
before acceptance; solo use requires an explicit waiver recorded in
the deviation log.

## Three-zone autonomy

Autonomy is zoned by risk; the V&V boundary is the automation boundary.

- Core / evidence zone (AI no access, human accountable): certified or
  qualified artifacts, evidence records, safety/security-critical code, and
  release baselines. AI must not read or write here without an explicit
  human-approved change request.
- Gray zone (AI assistant + HITL): AI plans and drafts; a human decides and
  approves each step. Architecture, requirements, tests with safety impact,
  and verification-affecting configuration live here.
- Non-critical zone (AI unrestricted): documentation, examples, scaffolding,
  low-risk refactors, and tooling glue.

This skill's outputs are treated as gray-zone by default; AI may draft but
a human approves. AI must never act autonomously in the core/evidence zone.

