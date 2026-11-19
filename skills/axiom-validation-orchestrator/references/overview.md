# axiom-validation-orchestrator: overview

Meta-skill that routes a verification target to the right execution engine and
generates the campaign skeleton.

## Routing table

- Unit / low-level C/C++ firmware -> Unity or GoogleTest (QEMU/Renode or JTAG/SWD).
- Developer integration / Embedded Linux -> Pytest plus Labgrid (containers, then physical DUT).
- System-level / HIL / acceptance -> Robot Framework with domain keywords.

## Campaign phases

1. Pre-check: bench readiness (instruments, rails, firmware hash).
2. Execution: cross-layer checks (SW logs plus HW stimulus simultaneously).
3. Triage: diagnostic bundle (last 100 UART lines, bus error counters, rail
   status) classified as Bench issue, Hardware fault, or Firmware regression.

## Chained skills

Flash via `axiom-firmware-lifecycle`, stimulate via
`axiom-hw-interface-control`, parse via `axiom-bus-protocol-validation`,
promote SIL cases via `axiom-sil-hil-bridge`.
