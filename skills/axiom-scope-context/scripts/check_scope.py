"""Scope artifact checker: envelope + boundary completeness."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from packages.skills.assurance import validate_artifact_file, load_doc


def check(doc: dict) -> list[str]:
    errors = []
    for field in ("system", "operating_context", "boundaries"):
        if field not in doc:
            errors.append(f"missing section: {field}")
    bounds = doc.get("boundaries", {}) or {}
    if not bounds.get("in_scope"):
        errors.append("boundaries.in_scope is empty")
    if not bounds.get("out_of_scope"):
        errors.append("boundaries.out_of_scope is empty")
    if (doc.get("system") or {}).get("name") in (None, "", "UNKNOWN"):
        errors.append("system.name is UNKNOWN")
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
