"""Validate an allocation record for axiom-aerospace-requirements-allocation.

Contract:
- No TODO markers may remain.
- Every data row must carry status ALLOCATED or UNALLOCATED.
- ALLOCATED rows must name an item and an owner.
- UNALLOCATED rows must carry a rationale (no bare N/A rationale).
- The completeness counts must reconcile.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def validate_record(path: str | Path) -> list[str]:
    errors: list[str] = []
    text = Path(path).read_text(encoding="utf-8")
    if "TODO" in text:
        errors.append("record contains unreplaced TODO markers")
    rows = [line for line in text.splitlines() if line.startswith("| SYS-REQ")]
    if not rows:
        errors.append("record contains no allocation rows")
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) < 6:
            errors.append(f"malformed row (expected 6 cells): {row[:60]}")
            continue
        _req, item, owner, _contract, status, rationale = cells[:6]
        if status not in {"ALLOCATED", "UNALLOCATED"}:
            errors.append(f"invalid status (must be ALLOCATED or UNALLOCATED): {row[:60]}")
        elif status == "ALLOCATED" and (item in {"N/A", ""} or owner in {"N/A", ""}):
            errors.append(f"ALLOCATED row missing item or owner: {row[:60]}")
        elif status == "UNALLOCATED" and rationale in {"N/A", ""}:
            errors.append(f"UNALLOCATED row missing rationale: {row[:60]}")
    counts = dict(re.findall(r"- (Baseline|ALLOCATED|UNALLOCATED) count: (\d+)", text))
    if len(counts) == 3:
        try:
            if int(counts["ALLOCATED"]) + int(counts["UNALLOCATED"]) != int(counts["Baseline"]):
                errors.append("completeness counts do not reconcile")
        except ValueError:
            errors.append("completeness counts are not integers")
    return errors


if __name__ == "__main__":
    problems = validate_record(sys.argv[1])
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("allocation record OK")
