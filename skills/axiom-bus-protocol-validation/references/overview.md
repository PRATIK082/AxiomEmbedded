# axiom-bus-protocol-validation: overview

Reusable frame builders and packet parsers for UART, CAN/CAN-FD, SPI, I2C,
Ethernet/MQTT, and BLE, with bidirectional checks.

## SW-to-HW direction

Firmware actions (register writes, state transitions, RTOS events) must
produce measurable physical outputs: voltages, PWM duty cycles, bus frames,
UART logs.

## HW-to-SW direction

Physical fault injection (brown-outs, sensor noise, bus shorts, packet drops)
must trigger expected firmware reactions: interrupts, error flags, recovery
states, DTCs where applicable.

## Rules

- Layouts come from the specification, never invented.
- Tolerances explicit; SIL tolerances widen on HIL promotion.
