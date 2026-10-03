# MPU skill

Microprocessor-based design with MMU, OS-hosted software, and external memory:
SoC selection, power and clock architecture, DDR and storage design, and the
hardware/software interface for Linux-capable targets.

## 1. Purpose and scope

**Purpose.** Select and integrate MPUs (Cortex-A, RISC-V application class)
so the software platform (`embedded-linux`, `robotics`) gets the memory,
I/O, and power behavior it was promised.

**In scope.** MPU selection criteria, MMU/memory-map planning, DDR sizing and
signal integrity, eMMC/NOR/NAND storage selection, PMIC and power sequencing,
clock trees, debug access (JTAG/SWD, trace), and HSI documentation.

**Non-goals.** MCU-only design (see `mcu`), silicon design. Ends at a reviewed
schematic, layout constraints, and a bring-up plan executed with
`hardware-bringup`.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | Arm Cortex-A / Armv8-A / Armv9-A | Current architecture references | MMU, exception levels, power domains | `https://developer.arm.com/documentation/` |
| 2 | RISC-V privileged ISA | Ratified v202401+ | Supervisor/machine modes, page-based virtual memory | `https://riscv.org/specifications/privileged-isa/` |
| 3 | JEDEC DDR4/DDR5 / LPDDR4/5 | JESD79-4/5 series | Timing, training, signal-integrity requirements | `https://www.jedec.org/standards-documents/` |
| 4 | JEDEC eMMC / UFS | JESD84 / JESD220 series | Managed-flash interface and endurance behavior | `https://www.jedec.org/standards-documents/` |

## 3. Selection rules

1. **Compute from measured load.** Size cores, clocks, and accelerators from
   profiled worst-case load (vision pipelines, control rates, network
   throughput) plus headroom — never from marketing DMIPS alone.
2. **Memory sized end to end.** DDR capacity covers OS + application + buffers
   + logging with margin; bandwidth validated against concurrent masters
   (CPU, GPU, NPU, DMA, display). LPDDR for power-constrained, DDR with ECC
   where reliability demands it (ECC is a safety/reliability requirement, not
   a luxury — see `safety` §5).
3. **Longevity checked first.** 10-year availability, second-source or
   pin-compatible alternatives, and the vendor's LTS kernel/BSP commitment
   (see `embedded-linux` §3) are selection gates, not afterthoughts.
4. **Security hardware required.** Secure boot ROM, OTP fuses, TRNG, and crypto
   acceleration are mandatory selection criteria for any connected product
   (consumed by `embedded-linux` §6 and `security`).

## 4. Integration discipline

1. **Power sequencing is a design artifact.** PMIC rails, reset timing, and
   power domains reviewed against the datasheet sequence; violations brick or
   age silicon — sequence verified on first Spin with a scope, not assumed
   from the reference schematic.
2. **DDR treated as high-speed design.** Length-matched, impedance-controlled
   routing per vendor guidelines; memory training validated across voltage
   and temperature corners; training failures are hardware defects, not
   software tunables.
3. **Clock tree documented.** Sources, PLLs, dividers, and jitter budgets per
   consumer (Ethernet, USB, audio, ADC); spread-spectrum settings recorded
   where EMC demands it.
4. **Debug designed in.** JTAG chain, SWD fallback, UART console, and trace
   (ETM/PTM pins or buffer) on every revision — depopulate, never delete.
   Undebuggable boards are schedule risks.

## 5. Handoff gates (blocking)

1. Schematic reviewed against datasheet checklists (power, DDR, clocks, reset,
   strapping pins) with dispositions.
2. Layout constraints (DDR, power integrity, EMC) issued to layout and
   verified on Gerbers.
3. Memory map (MMU regions, carveouts, secure vs non-secure) agreed with the
   software team and captured for the device tree (`embedded-linux` §4).
4. Bring-up plan written: staged power-on, bootloader port, memory test, and
   peripheral loopback sequence (executed with `hardware-bringup`).

## 6. Verification of this skill (Phase 4 gate)

- Selection criteria recorded with measurement or datasheet basis (§3).
- No layout tape-out without power/DDR/clock review evidence (§4–§5).
