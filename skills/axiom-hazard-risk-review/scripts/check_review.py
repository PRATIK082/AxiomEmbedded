"""Review-report checker: severity taxonomy, blocker actions, verdict consistency."""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from packages.skills.assurance import validate_artifact_file, load_doc

SEV = {"Blocker", "Major", "Minor", "Observation", "Information Request"}


def check(doc: dict) -> list[str]:
    errors = []
    findings = doc.get("findings")
    if not isinstance(findings, list):
        return ["findings list missing"]
    for f in findings:
        for key in ("id", "severity", "location", "recommendation", "owner"):
            if not f.get(key):
                errors.append(f"{f.get('id', '?')}: missing {key}")
        if f.get("severity") not in SEV:
            errors.append(f"{f.get('id', '?')}: bad severity")
    blockers = sum(1 for f in findings if f.get("severity") == "Blocker")
    if blockers and doc.get("verdict") != "revise-and-resubmit":
        errors.append("Blockers present but verdict is not revise-and-resubmit")
    if not findings and doc.get("verdict") != "accept":
        errors.append("no findings but verdict is not accept")
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
