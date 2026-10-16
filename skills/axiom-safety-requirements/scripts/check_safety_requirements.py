"""Safety-requirements checker: ID, hazard links, verification honesty."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from packages.skills.assurance import validate_artifact_file, load_doc


def check(doc: dict) -> list[str]:
    errors = []
    reqs = doc.get("requirements") or []
    if not reqs:
        errors.append("requirements list is empty")
    for r in reqs:
        if not str(r.get("id", "")).startswith("REQ-"):
            errors.append(f"bad requirement id {r.get('id')!r}")
        if not r.get("text") or r["text"] in ("UNKNOWN", "TBD"):
            errors.append(f"{r.get('id', '?')}: empty text")
        if r.get("verification") not in ("test", "inspection", "analysis", "OPEN"):
            errors.append(f"{r.get('id', '?')}: bad verification")
        if "TBD" in str(r.get("text", "")) and not doc.get("open_questions"):
            errors.append(f"{r.get('id', '?')}: TBD without open question")
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
