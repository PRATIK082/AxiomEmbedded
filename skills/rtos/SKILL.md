---
name: rtos
description: RTOS selection, scheduling/IPC rules, MPU partitioning, WCET verification. Use for FreeRTOS/Zephyr/ThreadX designs or timing analysis.
version: 1.3.0
domains: [all]
platforms: [mcu, mpu, rtos]
axiom:
  dotted_name: axiom.legacy.rtos
  domain: all
  subdomain: legacy
  category: legacy
  maturity: production
  owner: axiom-embedded
  tags:
  - legacy
  related_skills:
  - axiom-rtos-architecture
  checklists:
  - checklists/rtos-checklist.md
---

# rtos -- Real-time operating system capability (template replication 1)

Reusable AxiomEmbedded capability for RTOS selection, configuration,
scheduling analysis, and verification on MCU/MPU targets.

> Structure replicates the `mcu` template (see `docs/adr/0001-mcu-template.md`
> and `docs/adr/0002-rtos.md`). RTOS choice is safety-relevant: every
> scheduling decision must trace to a timing requirement.

## Objectives

- Select an RTOS (FreeRTOS 202604 LTS / Zephyr LTS / bare-metal) against
  determinism, footprint, safety, and ecosystem requirements.
- Configure tasks, priorities, IPC, timers, and memory protection (MPU regions).
- Prove schedulability (WCET budgets, priority assignment, stack sizing).
- Verify with host simulation, on-target timing tests, and fault injection.

## Prerequisites

- MCU capability delivered (`skills/mcu/`): clock tree, MPU, debug access.
- Timing requirements: periods, deadlines, jitter bounds per safety goal.
- Toolchain: `gcc-arm-none-eabi` or `clang`; CMake >= 3.20.
- Domain overlay loaded when applicable: `domains/automotive/`, `domains/aerospace/`, `domains/industrial/`.

## Outcomes

- `requirements/rtos-requirements.md` tracing SYS-xxx to RTOS-xxx (task sets, deadlines, ASIL/DAL).
- `architecture/rtos-architecture.md`: RTOS choice rationale, task/priority table, IPC map, MPU region plan.
- `src/` + `headers/` application tasks with Doxygen APIs, MISRA C:2025 clean.
- `test/` with host unit tests, timing tests, stack-overflow and deadline-miss injection.
- `build/` CMake project, zero warnings with `-Wall -Wextra -Werror` on gcc and clang.
- `evidence/` linking every claim to a standard clause and a test result.

## Time estimate

- Selection + architecture: 2-3 days. Configuration + integration: 3-5 days. Timing verification: 3-5 days.

## Resources

- FreeRTOS 202604 LTS (kernel 11.3.0, security hardening, expanded MPU support,
  MQTT v5.0, supported to 2028-04-30):
  `https://www.freertos.org/Community/Blogs/2026/freertos-202604-lts-now-available`
- FreeRTOS LTS libraries and changelog:
  `https://github.com/FreeRTOS/FreeRTOS-LTS/blob/202604-LTS/CHANGELOG.md`
- Zephyr documentation (v4.x, 3.7 LTS lineage, 1000+ boards, POSIX PSE51/PSE52 subsets,
  tickless scheduler, Kconfig/Devicetree):
  `https://docs.zephyrproject.org/latest/index.html`
- Zephyr 2025 overview (LTS 2+ year policy, West meta-tool, power management):
  `https://www.zephyrproject.org/wp-content/uploads/2025/06/Zephyr-Overview-20250626.pdf`
- MISRA C:2025: `https://misra.org.uk/misra-c`

## RTOS selection guide

| Option | Use when |
| --- | --- |
| Bare-metal | Timing analysis proves a super-loop/event core meets all deadlines; smallest footprint |
| FreeRTOS 202604 LTS | Preemptive scheduling, MPU task isolation, MQTT/IoT libraries, 2-year LTS stability to 2028-04-30 |
| Zephyr LTS | POSIX subsets ease porting, Devicetree + 1000+ board support, tickless low-power scheduler, native Linux emulation for host tests |

## Scheduling and IPC rules

- Fixed-priority preemptive by default; document every priority assignment against
  rate-monotonic or deadline-monotonic analysis.
- Priority inheritance (or ceiling) on every mutex shared across priorities -- no
  unbounded priority inversion.
- Prefer queues/message-passing over shared memory; guard shared state with
  explicit ownership (`rules/baseline.yaml`: no-implicit-state, explicit-error-handling).
- Bound every ISR and deferred handler (max complexity 15); ISRs signal, tasks work.
- Size every stack analytically plus guard regions; prove overflow detection
  (MPU guard or stack watermark checked in test).

## Memory protection

- FreeRTOS 202604 LTS claims fewer MPU regions -- reserve the remainder for
  application task isolation (kernel/flash, task stacks, peripheral guards).
- Unprivileged tasks by default; privilege escalation only via audited gates.
- Map claims to `rules/security.yaml` and the active domain overlay.

## Timing verification

- WCET budget per task; measured worst-case on target plus margin, recorded in `evidence/`.
- Deadline-miss injection (`skills/fault-injection/`): overload, ISR storm, clock drift.
- Watchdog strategy: task-aware (window/checkpoint) rather than a blind kick.
- Coverage targets from `configs/skill-update.yaml`: ASIL A/DAL D 100% statement+branch;
  ASIL B/DAL C adds recommended MC/DC; ASIL C-D/DAL A-B requires MC/DC.

## Build

- `cmake_minimum_required(VERSION 3.20)`; presets for `debug`, `release`, `hil`.
- Flags: `-Wall -Wextra -Werror` on gcc and clang.
- FreeRTOS: pin the `202604.01-LTS` tag; Zephyr: pin West manifest revision -- never float.
- Static analysis in CI: MISRA checker + `rules/c.yaml` + `rules/embedded-baseline.yaml`.

## Test strategy

- Host: unit tests with mocked kernel ports; Zephyr native-emulation runs for logic.
- Target: timing tests (logic-analyzer or cycle-counter traces), MPU-fault tests,
  stack-guard tests, tickless-sleep current measurement.
- HIL: full task set under injected faults; watchdog and brown-out recovery proven.

## Traceability

- `traceability-matrix.schema.json`: every SYS-xxx -> RTOS-xxx -> `src/` file -> `test/` case -> evidence id.
- No orphan task, no orphan test. `scripts/verify_skill.py --skill rtos` enforces presence.

## Compliance mapping (via domain overlays, not duplication)

- Automotive: ISO 26262-6 software level (ASIL A-D); scheduling freedom-from-interference
  argued in the overlay, not here.
- Aerospace/defense: DO-178C objectives per DAL; tool qualification via DO-330 where claimed.
- Industrial: IEC 61508 SIL via `domains/` overlays. Never claim certification from this
  heuristic skill -- produce audit-ready evidence only.

## Verification checklist (gate: all must pass)

1. `scripts/verify_skill.py --skill rtos` -> PASS.
2. CMake configure + build, gcc and clang, zero warnings.
3. Unit + timing tests green at the required coverage.
4. MISRA C:2025 scan: zero mandatory/required violations or deviated with rationale.
5. Traceability matrix complete; standards cited with number + version + clause + URL.
6. Scheduling/timing deltas flagged for human review before PR (safety-relevant).

Load task-specific domain/platform/rule overlays before execution.



## 7. RTOS task architecture rules

### 7.1 One task, one responsibility
Each task owns exactly one functional domain. Forbidden: monolithic super-task mixing sensor read, PID, OLED, UART, flash in one loop. Decompose into sensor_task, control_task, telemetry_task, logger_task.

### 7.2 Task classification
- **Acquisition task** (imu_task, adc_task, encoder_task, gps_task): acquire raw data, publish via queue/event. Must not contain control algorithms, logging, or protocol processing.
- **Control task** (attitude_task, motor_control_task, balance_task): compute control outputs, enforce timing via `osDelayUntil`/`vTaskDelayUntil`. Must not contain SPI/I2C register access, display refresh, file I/O.
- **Communication task** (uart_task, can_task, usb_task, ethernet_task): protocol encoding/decoding, buffer management, forward data to queues. Must not contain control law or business logic.
- **Service task** (logger_task, storage_task, monitor_task, health_check_task): background housekeeping, health monitoring, logging. Must not contain real-time control or sensor acquisition.

### 7.3 Scheduling rules
Periodic tasks must use fixed-rate scheduling (`osDelayUntil`/`vTaskDelayUntil`), not `osDelay` (which drifts by execution time).

### 7.4 Priority rules
Assign priority by real-time criticality: Control Task (highest) -> Sensor Task -> Communication Task -> Service/Logging Task -> Idle. Control-related interrupts must have higher priority than communication interrupts.

### 7.5 Inter-task communication rules
Shared data between tasks must never use bare global variables. Use:
- Queue -- for data streams (`imu_task -> [queue] -> control_task`).
- Event flags -- for state notification (DMA complete, data ready, GPS lock).
- Mutex -- for shared resources (flash, SD card, shared buffer). Do not use mutex as message-passing.
ISR-to-task handoff via queue/event (`FromISR` APIs), not shared globals.

### 7.6 ISR cooperation rules
ISRs must be minimal. Allowed: set event flag, send to queue (ISR-safe API), release semaphore (ISR-safe), start DMA. Forbidden in ISR: `printf`, `malloc`/`free`, floating-point math, protocol parsing, control algorithm math, blocking calls. DMA post-processing runs in task context, not ISR.

### 7.7 Resource ownership rules
Every hardware resource has exactly one owning task. Multiple tasks must not write the same UART directly; route through a single owner via queue.

### 7.8 Watchdog rules
Every RTOS project must include a watchdog/health-monitor: task liveness heartbeats, queue depth checks, stack high-water marks.

### 7.9 Timing documentation
Document per periodic task: Task, Hz, Priority, Stack, WCET (worst-case execution time).

### 7.10 RTOS validation checklist
- [ ] Each task has single, clearly defined responsibility
- [ ] No super-tasks mixing acquisition, control, communication
- [ ] Periodic tasks use `osDelayUntil`/`vTaskDelayUntil`
- [ ] Priorities assigned by real-time criticality
- [ ] ISRs contain no printf, malloc, float math, protocol parsing, control logic
- [ ] ISR-to-task handoff via queue or event
- [ ] Inter-task communication uses queues/events/mutexes, not bare extern globals
- [ ] Control loops not coupled to communication timing
- [ ] DMA post-processing in task context
- [ ] Each hardware resource has single owning task
- [ ] Watchdog/health monitor exists
- [ ] Timing parameters (period, priority, stack, WCET) documented

### 7.11 Auto-fix strategy
Identify task responsibility overlap or ISR overreach; split monolithic tasks; replace bare global sharing with queues/events/mutexes; move heavy ISR work into task context via deferred processing; introduce resource ownership model; reassign priorities; regenerate RTOS architecture and task documentation.

## 8. ISR design rules (Fast In, Fast Out)

### 8.1 Core principle
ISRs capture events; tasks process business logic. ISRs measured in microseconds.

### 8.2 Allowed in ISR (event capture only)
Read hardware status register, clear interrupt flag, capture timestamp, copy bounded data to buffer, set event flag, send to queue, give semaphore, start DMA, wake task, increment bounded counter.

### 8.3 Forbidden in ISR (business processing)
Protocol parsing, attitude estimation, PID/control law, Kalman filter, path planning/navigation, file system ops, flash write/erase, network processing, display refresh, logging, complex loops with non-constant bounds, blocking calls.

### 8.4 Execution time budget
| ISR Type | Max recommended |
|----------|-----------------|
| GPIO | < 5 us |
| UART | < 10 us |
| SPI | < 10 us |
| DMA | < 10 us |
| I2C | < 15 us |
| CAN | < 20 us |
| Timer | < 20 us |
No unbounded loops in ISR.

### 8.5 Strict rules
- `printf` strictly forbidden in ISR (blocking, non-deterministic, not reentrant).
- `malloc`/`calloc`/`realloc`/`free` forbidden in ISR.
- Extensive floating-point math forbidden in ISR.
- HAL blocking operations (`HAL_UART_Transmit` with timeout, `HAL_Delay`) forbidden; dispatch calls (`HAL_UART_IRQHandler`) allowed.
- RTOS integration must use `FromISR` variants (`xQueueSendFromISR`, `vTaskNotifyGiveFromISR`, `xSemaphoreGiveFromISR`, `portYIELD_FROM_ISR`).
- Interrupt priority reflects real-time criticality: Timer Control (highest) -> DMA -> SPI/I2C -> UART -> EXTI (lowest). Control interrupts higher than communication.
- Shared data must use queue, double buffer, or event flag -- not unstructured shared globals. Ring buffer for UART RX.
- Timer ISR: only system tick, periodic event flags, input capture timestamps, counter increment. No PID, telemetry, sensor fusion.

### 8.6 ISR patterns
- Flag pattern (single binary event)
- Queue pattern (data streaming)
- Event pattern (task notification)
- Ring buffer pattern (buffered UART RX)

### 8.7 Flight controller special rules
Forbidden: running Mahony/PID inside IMU data-ready ISR (`IMU IRQ -> Mahony -> PID -> PWM` all in ISR). Required: `IMU IRQ -> [TaskNotify] -> Control Task (1 kHz) -> Mahony -> PID -> PWM`.

### 8.8 ISR validation checklist
- [ ] ISR has single, clearly defined responsibility
- [ ] ISR execution time bounded and predictable
- [ ] No complex loops with variable bounds
- [ ] No protocol parsing in ISR
- [ ] No control algorithm computation in ISR
- [ ] No printf or logging in ISR
- [ ] No malloc/free or heap operations in ISR
- [ ] No blocking calls in ISR
- [ ] RTOS FromISR APIs used where applicable
- [ ] Interrupt flag correctly cleared
- [ ] Event notification or queue used for ISR->task handoff
- [ ] ISR responsibilities separated from task responsibilities
- [ ] No business logic in ISR
- [ ] DMA ISR defers processing to task context
- [ ] if RTOS: portYIELD_FROM_ISR() called when task wake requested

### 8.9 Auto-fix strategy
Identify heavy operations in ISR; move into task context; replace direct shared-variable communication with queue/event/ring buffer; replace blocking APIs with non-blocking or FromISR variants; introduce ring buffer for serial data; recalculate worst-case interrupt latency; revalidate.

