# diag-extract-bridge

Example bridge: maps an **external, independently-developed** pip pack that
extracts diagnostic data (ARXML incl. all types, ODX/PDX, CDD, XLS/XLSX, all
supported AUTOSAR versions) into the internal canonical YAML/JSON
(`schemas/uds-test-spec.schema.json`).

The pack below is an exemplar (`acme-diag-extract`). Substitute any real
pack implementing the same entry-point contract — the bridge is unchanged.

## Install (external pack, independent release cycle)

```bash
pip install "acme-diag-extract>=2.1,<3"
```

## Use

```bash
python tools/diag-extract-bridge/bridge.py --in diag_extract.arxml --out spec.yaml
# then feed the spec to the generator:
python tools/diag-uds-testgen/generate_uds_tests.py --spec spec.yaml --out out/DoorECU --ecu DoorECU
```

Without the pack installed the bridge fails closed with the install hint.
Pack version, input hash, and output hash are recorded in the spec
`provenance` block for `skills/evidence/` traceability.

Input/output contracts are schema-backed and deterministic.
See `docs/external-packs.md` for the link-don't-bundle policy.
