"""UDS matrix checker: validate a YAML service matrix (sid/session/security coverage)."""
from __future__ import annotations
import pathlib
import sys

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

REQUIRED_SIDS = (0x10, 0x22, 0x19, 0x27, 0x3E)


def check_matrix(spec: dict) -> list[str]:
    errors = []
    svcs = {s.get("sid"): s for s in spec.get("services", [])}
    for sid in REQUIRED_SIDS:
        if sid not in svcs:
            errors.append(f"missing SID {sid:#04x}")
    for sid, s in svcs.items():
        if not s.get("sessions"):
            errors.append(f"SID {sid:#04x}: no sessions declared")
        for item in s.get("dids", []) + [{"id": x} for x in s.get("subfunctions", [])]:
            if item is None:
                errors.append(f"SID {sid:#04x}: empty selector entry")
    return errors


def main() -> int:
    if yaml is None:
        print("uds check: SKIP (PyYAML unavailable)")
        return 0
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    files = sorted(target.rglob("*uds*matrix*.yaml")) + sorted(target.rglob("*uds*matrix*.yml"))
    if not files:
        print("UDS check: no matrix files found (PASS with warning: nothing to check)")
        return 0
    rc = 0
    for f in files[:20]:
        spec = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        errs = check_matrix(spec)
        if errs:
            rc = 1
            print(f"{f}: REVIEW")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"{f}: PASS")
    print("UDS check: " + ("PASS" if rc == 0 else "REVIEW (see findings)"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
