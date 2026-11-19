# axiom-hw-interface-control: overview

Physical bench ownership for HIL campaigns. One file, `board_config.yaml`,
maps logical channel names to physical interfaces; everything else references
logical names.

## Supported channel kinds

- `serial`: UART console / log capture (`port`, `baud`).
- `scpi`: power supplies and instruments over VISA (`visa` string).
- `relay`: programmable relays for power and fault injection (`board`, `channel`).
- `scope`: oscilloscope channels for voltage/timing capture (`visa`, `channel`).
- `analyzer`: logic analyzer pods for protocol capture.

## Session contract

1. Pre-check (ping, rails, firmware hash).
2. Idempotent setup (all channels to safe state).
3. Execute (stimulus plus capture).
4. Fail-safe teardown (unconditional; report always written).
