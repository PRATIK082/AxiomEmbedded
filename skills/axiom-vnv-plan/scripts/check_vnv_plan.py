"""V&V-plan checker: coverage matrix + no invented passes."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from packages.skills.assurance import validate_artifact_file, load_doc


def check(doc: dict) -> list[str]:
    errors = []
    cases = doc.get("test_cases") or []
    matrix = doc.get("trace_matrix") or []
    if not cases:
        errors.append("test_cases list is empty")
    for t in cases:
        if not str(t.get("id", "")).startswith("TEST-"):
            errors.append(f"bad test id {t.get('id')!r}")
        if t.get("result") not in ("not-run", "pass", "fail", "OPEN"):
            errors.append(f"{t.get('id', '?')}: bad result")
        if t.get("result") == "pass" and "EVD-" not in str(doc.get("evidence", [])):
            errors.append(f"{t.get('id', '?')}: pass claimed without EVD evidence")
    mapped = {str(r.get("test_case")) for r in matrix if isinstance(r, dict)}
    for t in cases:
        if isinstance(t, dict) and t.get("id") not in mapped:
            errors.append(f"{t['id']}: missing from trace_matrix")
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
