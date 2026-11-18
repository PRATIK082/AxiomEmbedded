"""Validate an applicability matrix: verdict contract, no TODOs, no DAL claims."""
from __future__ import annotations

import re
import sys
from pathlib import Path

VERDICTS = {"APPLICABLE", "NOT_APPLICABLE", "DEFERRED"}
FORBIDDEN = re.compile(r"\bTODO\b", re.IGNORECASE)
DAL_CLAIM = re.compile(r"\bDAL\s+[A-E]\s+(assigned|upgraded|downgraded)\s+by\s+this", re.IGNORECASE)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if FORBIDDEN.search(text):
        errors.append("matrix still contains TODO placeholders")
    rows = [l for l in text.splitlines() if l.startswith("|")][2:]
    if not rows:
        errors.append("matrix has no standard rows")
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) < 5:
            errors.append(f"malformed row: {row}")
            continue
        if cells[3] not in VERDICTS:
            errors.append(f"invalid verdict {cells[3]!r} in row: {row}")
        if not cells[4] or cells[4] == "TODO":
            errors.append(f"missing rationale in row: {row}")
    if DAL_CLAIM.search(text):
        errors.append("matrix claims DAL assignment by this skill")
    return errors


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("templates/applicability-matrix.md")
    problems = validate(target)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("matrix valid")
