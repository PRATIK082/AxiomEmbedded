# Board configuration: {{dut_name}} (schema v{{schema_version}})

Channels: {{channel_count}} logical / {{physical_count}} physical
Safe state: {{safe_state_summary}}

## Pre-check

- [ ] All instruments pinged
- [ ] DUT rails nominal ({{rail_readings}})
- [ ] Firmware hash {{firmware_hash}}

## Teardown report

- Relays: {{relay_state}} / DUT reset: {{reset_method}} / Buffers flushed: yes

Evidence: run-manifest.json
