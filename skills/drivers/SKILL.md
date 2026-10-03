# Drivers skill

Peripheral driver development for MCU/MPU targets: register-correct,
interrupt-safe, DMA-disciplined drivers with HAL interfaces that keep policy
out and make hardware testable without hardware.

## 1. Purpose and scope

**Purpose.** Deliver drivers that are correct against the reference manual,
safe under concurrency, bounded in timing, and mockable for host-side testing.

**In scope.** Memory-mapped register practice, clock/reset/GPIO setup, UART/
SPI/I2C/CAN/ADC/PWM/timer drivers, DMA design, interrupt handling, error
recovery, HAL interface shape, and driver-level testing with mocks and logic
analyzers.

**Non-goals.** Application policy built on drivers (see `implementation`) and
Linux kernel driver subsystems (see `embedded-linux` §4). Ends at reviewed,
measured, unit-tested drivers behind stable HAL interfaces.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | MISRA C | MISRA C:2025 (current) | Register access, volatile discipline, documented deviations | `https://misra.org.uk/` |
| 2 | CMSIS | v6.x (Arm Cortex-M software interface) | Standard peripheral access shape for Cortex-M targets | `https://www.keil.arm.com/cmsis/` |
| 3 | Target reference manual | Silicon-vendor current | Register maps, clock trees, errata — the binding truth | Vendor documentation portal |

> The reference manual plus errata outranks every example, HAL library, and
> forum post. Silicon bugs live in errata; drivers implement the workarounds.

## 3. Register and init discipline

1. **Read the manual section twice.** Clock gating, reset release, and pin
   multiplexing precede any peripheral register touch; reserved bits written
   as specified (usually preserve-on-write), never blindly zeroed.
2. **Structured access.** Register maps as `volatile`-qualified structs or
   CMSIS headers; magic addresses and bit numbers appear exactly once as
   named constants. Bit manipulation through helpers with width/mask checks.
3. **Errata first.** The silicon errata is read before driver design starts;
   each applicable item gets a workaround with a comment citing the errata ID,
   and a test where the workaround is observable.

## 4. Interrupts, DMA, and timing

1. **Interrupt ownership.** Each peripheral interrupt has one owner, one
   priority justified against the latency budget (`bare-metal` §4), and a
   measured worst-case handler duration.
2. **DMA by contract.** Buffer ownership (CPU vs DMA) explicit at every
   handoff; cache maintenance (clean/invalidate) at boundaries on cached
   targets; transfer-complete/error/timeout paths all handled and tested —
   the error IRQ is wired up, not left disabled.
3. **Timeouts everywhere.** Every busy-wait and every blocking poll carries a
   timeout derived from the peripheral's timing plus margin; timeout expiry
   produces a diagnosed error, never a hang.

## 5. HAL shape and testability

1. **Policy-free drivers.** Drivers move bytes and signal events; retries,
   protocols, and application state machines live above the HAL. A driver that
   implements product behavior fails review.
2. **Mockable seams.** Register backends injected (base-address parameters or
   link-time seams) so unit tests drive the driver against scripted register
   models on host, including fault injection (NACK, overrun, DMA error).
3. **Proven on wire.** Logic-analyzer or scope captures confirm timing-critical
   protocols (I2C clock stretch, SPI modes, CAN bit timing) on real hardware;
   captures are release evidence for new drivers.

## 6. Release gates (blocking)

1. Register practice reviewed against manual + errata with cited workarounds.
2. Interrupt priorities justified; handler durations measured.
3. DMA ownership and cache discipline documented; error paths tested.
4. Timeouts on every wait; no unbounded busy-loops.
5. Host unit tests with register-model fault injection green.
6. Protocol captures on hardware for timing-critical drivers.

## 7. Verification of this skill (Phase 4 gate)

- Errata compliance is auditable per driver (§3.3).
- Concurrency and timing evidence measured on target (§4), not assumed.
