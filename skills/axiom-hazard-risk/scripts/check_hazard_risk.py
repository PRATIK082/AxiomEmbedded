"""Hazard-risk checker: severity/control/rationale completeness."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from packages.skills.assurance import validate_artifact_file, load_doc


def check(doc: dict) -> list[str]:
    errors = []
    hazards = doc.get("hazards") or []
    if not hazards:
        errors.append("hazards list is empty")
    for h in hazards:
        if not str(h.get("id", "")).startswith("HAZ-"):
            errors.append(f"bad hazard id {h.get('id')!r}")
        if h.get("severity") not in ("low", "medium", "high", "critical"):
            errors.append(f"{h.get('id', '?')}: bad severity")
    return errors


def main() -> int:
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    files = [target] if target.is_file() else sorted(target.glob("*.yaml")) + sorted(target.glob("*.yml"))
    rc = 0
    for f in files[:20]:
        rep = validate_artifact_file(f)
        extra = check(load_doc(pathlib.Path(f)))
        errs = rep["errors"] + extra
        print(f"{f}: {'PASS' if not errs else 'REVIEW'}")
        for e in errs:
            print(f"  - {e}")
        rc = rc or bool(errs)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
