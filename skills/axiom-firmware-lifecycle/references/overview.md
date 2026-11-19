# axiom-firmware-lifecycle: overview

Source-to-target ownership: reproducible build, signing, flashing, reset,
attestation.

## Vendor paths

- Cortex-M via probe: OpenOCD or J-Link flash, probe reset, boot-log capture.
- DFU-capable MCU: DFU-util over USB, re-enumeration check.
- Embedded Linux MPUs: U-Boot/TFTP or SD image, relay power-cycle, boot prompt.

## Identity contract

Every image carries hash plus build provenance. Campaign pre-checks gate on
this identity; a hash mismatch blocks execution before any test runs.
