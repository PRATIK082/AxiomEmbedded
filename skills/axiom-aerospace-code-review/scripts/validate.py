"""Validate a filled review record against the verdict contract."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REQUIRED_GATES = [
    "scope-dal", "entry-criteria", "independence", "hlr-quality",
    "traceability", "code-compliance", "verification-artifacts",
    "findings-classified", "dal-unchanged", "verdict-record",
]


def validate_record(path: str | Path) -> list[str]:
    errors: list[str] = []
    text = Path(path).read_text(encoding="utf-8")
    if "TODO" in text:
        errors.append("record contains unfilled TODO placeholders")
    for gate in REQUIRED_GATES:
        if gate not in text:
            errors.append(f"missing gate: {gate}")
    if "verdict:" not in text:
        errors.append("missing verdict line")
    if "dal:" not in text:
        errors.append("missing DAL line")
    return errors


if __name__ == "__main__":
    errs = validate_record(sys.argv[1])
    if errs:
        print("\n".join(errs))
        raise SystemExit(1)
    print("record OK")
