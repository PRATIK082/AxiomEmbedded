"""Validate a filled applicability matrix (verdict contract check)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED = {"APPLICABLE", "NOT_APPLICABLE", "DEFERRED"}
ROW_RE = re.compile(r"^\|\s*([a-z0-9][a-z0-9\-]*)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$")


def validate_matrix(path: Path) -> list[str]:
    errors: list[str] = []
    rows = 0
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        if set(m.group(1).lower()) <= set("|- "):
            continue
        rows += 1
        std_id, _edition, verdict, governor, rationale = (g.strip() for g in m.groups())
        if verdict not in ALLOWED:
            errors.append(f"line {lineno}: {std_id}: verdict {verdict!r} not in {sorted(ALLOWED)}")
            continue
        if not rationale:
            errors.append(f"line {lineno}: {std_id}: missing rationale")
        if verdict == "APPLICABLE" and not governor:
            errors.append(f"line {lineno}: {std_id}: APPLICABLE needs a governing scope/plan")
    if rows == 0:
        errors.append("no matrix rows found")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print("usage: validate.py --matrix <filled-matrix.md>")
        return 2
    if argv[0] != "--matrix":
        print("usage: validate.py --matrix <filled-matrix.md>")
        return 2
    errors = validate_matrix(Path(argv[1]))
    for e in errors:
        print(f"ERROR: {e}")
    print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
