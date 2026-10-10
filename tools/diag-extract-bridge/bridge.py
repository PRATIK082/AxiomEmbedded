"""Bridge shim: external diag-extract pack -> canonical UDS test-spec.

Contract (see docs/external-packs.md):
- The external pack owns ALL format knowledge (ARXML types/versions, ODX,
  CDD, XLSX). This file only imports its entry point, validates the shape
  against the canonical spec, and stamps provenance.
- Fails closed when the pack is missing, with the install hint.
- Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path

BRIDGE_ID = "diag-extract-bridge"
BRIDGE_VERSION = "1.0.0"
ENTRY_POINT = "acme_diag_extract.extract"
PIP_SPEC = "acme-diag-extract>=2.1,<3"

REQUIRED_SPEC_KEYS = ("ecu", "services")


def load_pack_entry_point():
    """Import the external pack entry point or raise an actionable error."""
    mod_name, _, func_name = ENTRY_POINT.partition(".")
    try:
        mod = importlib.import_module(mod_name)
    except ImportError as exc:
        raise SystemExit(
            f"{BRIDGE_ID}: external pack missing ({exc}). "
            f"Install it independently: pip install \"{PIP_SPEC}\""
        ) from exc
    try:
        return getattr(mod, func_name)
    except AttributeError as exc:
        raise SystemExit(
            f"{BRIDGE_ID}: pack installed but entry point '{ENTRY_POINT}' "
            f"not found. Check pack version compatibility."
        ) from exc


def validate_spec_shape(spec: dict, source: str) -> None:
    missing = [k for k in REQUIRED_SPEC_KEYS if k not in spec]
    if missing:
        raise SystemExit(f"{BRIDGE_ID}: pack output from {source} missing keys: {missing}")
    services = spec.get("services", [])
    if not isinstance(services, list) or not services:
        raise SystemExit(f"{BRIDGE_ID}: pack output from {source} has no services")
    for i, svc in enumerate(services):
        if "sid" not in svc or "name" not in svc:
            raise SystemExit(f"{BRIDGE_ID}: service #{i} from {source} lacks sid/name")


def run(in_path: Path, out_path: Path) -> dict:
    extract = load_pack_entry_point()
    spec = extract(str(in_path))
    if not isinstance(spec, dict):
        raise SystemExit(f"{BRIDGE_ID}: entry point must return a dict, got {type(spec).__name__}")
    validate_spec_shape(spec, in_path.name)
    try:
        pack_version = importlib.metadata.version(PIP_SPEC.split(">")[0].split("<")[0].split("=")[0])
    except Exception:  # noqa: BLE001
        pack_version = "unknown"
    spec.setdefault("provenance", {}).update({
        "source_file": in_path.name,
        "bridge": f"{BRIDGE_ID} {BRIDGE_VERSION}",
        "pack": ENTRY_POINT,
        "pack_version": pack_version,
        "input_sha256": hashlib.sha256(in_path.read_bytes()).hexdigest(),
    })
    out_path.write_text(json.dumps(spec, indent=2, sort_keys=True), encoding="utf-8")
    return {"bridge": BRIDGE_ID, "pack_version": pack_version,
            "spec": out_path.name,
            "output_sha256": hashlib.sha256(out_path.read_bytes()).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser(description="Bridge external diag-extract pack to canonical spec.")
    ap.add_argument("--in", dest="in_path", required=True)
    ap.add_argument("--out", dest="out_path", required=True)
    args = ap.parse_args()
    info = run(Path(args.in_path), Path(args.out_path))
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
