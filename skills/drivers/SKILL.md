---
name: drivers
description: Register/errata discipline, DMA contracts, timeouts, policy-free HALs. Use when writing peripheral drivers or BSPs.
version: 1.3.0
domains: [all]
platforms: [mcu, mpu, soc]
axiom:
  dotted_name: axiom.legacy.drivers
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills:
  - axiom-embedded-firmware-bringup
  checklists:
  - checklists/drivers-checklist.md
---

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
Linux kernel driver subsystems (see `embedded-linux` S4). Ends at reviewed,
measured, unit-tested drivers behind stable HAL interfaces.

## 2. Normative sources (high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | MISRA C | MISRA C:2025 (current) | Register access, volatile discipline, documented deviations | `https://misra.org.uk/` |
| 2 | CMSIS | v6.x (Arm Cortex-M software interface) | Standard peripheral access shape for Cortex-M targets | `https://www.keil.arm.com/cmsis/` |
| 3 | Target reference manual | Silicon-vendor current | Register maps, clock trees, errata -- the binding truth | Vendor documentation portal |

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
   priority justified against the latency budget (`bare-metal` S4), and a
   measured worst-case handler duration.
2. **DMA by contract.** Buffer ownership (CPU vs DMA) explicit at every
   handoff; cache maintenance (clean/invalidate) at boundaries on cached
   targets; transfer-complete/error/timeout paths all handled and tested --
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

- Errata compliance is auditable per driver (S3.3).
- Concurrency and timing evidence measured on target (S4), not assumed.



## 7. Layered driver architecture rules

### 7.1 Layer stack
```
APP -> MODULE (business logic) -> INTERFACE (contracts) -> DEVICE DRIVER -> BUS DRIVER -> HAL/BSP -> STM32 HAL/CMSIS
```
Forbidden: IMU driver calling HAL directly (couples device driver to one MCU family).

### 7.2 Driver classification
- **Bus driver** (`driver/bus/`): bus protocol on a specific MCU (SPI, I2C, UART, CAN, USB, ETH).
- **Device driver** (`driver/device/`): specific chip (ICM42688, MPU6050, W25Q64, BMP280, SX1278).
- **BSP driver** (`bsp/`): board-level resources (LED, Button, Buzzer, OLED). BSP items belong under `bsp/`, not `driver/`.

Device drivers must never contain: PID controller logic, Kalman filter, attitude estimation, navigation algorithms, application state machines.

### 7.3 Required directory structure
```
driver/
"oe"EUR"EUR bus/
"'   "oe"EUR"EUR spi/  i2c/  uart/  can/
"oe"EUR"EUR device/
"'   "oe"EUR"EUR icm42688/  (icm42688.c, .h, _reg.h)
"'   "oe"EUR"EUR w25qxx/
"'   """EUR"EUR bmp280/
"""EUR"EUR common/
    "oe"EUR"EUR error.h  types.h
```

### 7.4 Bus abstraction rules
Every bus must expose an abstract interface; device drivers depend only on these, never on vendor HAL types.
- SPI: `spi_if_t` with `transfer`, `transfer_async`.
- I2C: `i2c_if_t` with `write`, `read`, `write_read`.
Forbidden in device drivers: `SPI_HandleTypeDef`, `HAL_SPI_Transmit()`. Required: `spi->transfer(tx, rx, len)`.

### 7.5 Device context rules
Driver state must live in a device context struct, not globals. Enables multiple instances on different bus channels.

### 7.6 Initialization rules
Unified init interface: `error_t xxx_init(xxx_t *dev)`. Hidden global state (`void imu_init(void)`) is forbidden.

### 7.7 Register encapsulation rules
Register addresses and bit-fields must be centralized in a `_reg.h` header. No magic register addresses scattered in driver code.

### 7.8 Synchronization and DMA rules
Device drivers must not be aware of DMA streams/channels or IRQ numbers. Bus interface exposes sync and async transfer; device driver chooses mode but does not configure DMA hardware. RTOS concerns (blocking, yielding, mutex) handled by layer above.

### 7.9 RTOS isolation rules
Device drivers must be RTOS-agnostic: no `osDelay`, `vTaskDelay`, `osMutexAcquire`, no busy-wait loops. Use timeout/callback/event mechanisms instead.

### 7.10 Error handling rules
All drivers use unified `error_t` enum (`ERR_OK`, `ERR_TIMEOUT`, `ERR_BUSY`, `ERR_INVALID_PARAM`, `ERR_NOT_READY`, `ERR_COMMUNICATION`). No magic `-1`/`-2`.

### 7.11 Mock testing rules
Every bus interface must be mockable (function-pointer struct) so device drivers can be tested on PC without MCU hardware.

### 7.12 Validation checklist
- [ ] Device driver contains no HAL API calls
- [ ] Device driver contains no MCU-specific types
- [ ] Device driver depends on bus interface, not MCU bus peripheral
- [ ] No magic register addresses -- all in `_reg.h`
- [ ] Register bit definitions are named constants
- [ ] Device state is in a context struct, not globals
- [ ] No global `static` device state
- [ ] Init interface follows `error_t xxx_init(xxx_t *dev)`
- [ ] Error codes are typed (`error_t`), not magic `-1`/`-2`
- [ ] No DMA configuration inside device driver
- [ ] No IRQ numbers inside device driver
- [ ] No RTOS calls in driver code
- [ ] No busy-wait loops
- [ ] Bus interface supports mock injection
- [ ] Driver contains no PID, Kalman, or control algorithm logic

### 7.13 Auto-fix strategy
Identify HAL/register leakage; extract bus operations into `spi_if_t`/`i2c_if_t`; move register constants into `_reg.h`; encapsulate global state into context struct; replace magic error codes with `error_t`; remove DMA/IRQ/RTOS dependencies; separate control algorithms into `module/`.

