"""Threat-model checker: interface coverage + control honesty."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from packages.skills.assurance import validate_artifact_file, load_doc


def check(doc: dict) -> list[str]:
    errors = []
    threats = doc.get("threats") or []
    if not threats:
        errors.append("threats list is empty")
    for t in threats:
        if not str(t.get("id", "")).startswith("SEC-"):
            errors.append(f"bad threat id {t.get('id')!r}")
        if t.get("severity") not in ("low", "medium", "high", "critical"):
            errors.append(f"{t.get('id', '?')}: bad severity")
        if not t.get("controls") and "OPEN" not in str(t.get("verification", "")) \
                and not doc.get("open_questions"):
            errors.append(f"{t.get('id', '?')}: no controls and no open question")
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
