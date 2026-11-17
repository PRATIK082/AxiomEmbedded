"""Validate a verification verdict record.

Contract: every coverage row has requirement_id and a status from the
allowed set; WAIVED rows need a matching waiver entry with justification
and approval_ref; verdict must be one of VERIFIED, PARTIAL, BLOCKED.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ALLOWED_STATUS = {"VERIFIED", "FAILED", "BLOCKED", "WAIVED", "NOT_APPLICABLE"}
ALLOWED_VERDICT = {"VERIFIED", "PARTIAL", "BLOCKED"}


def validate_record(path: str | Path) -> list[str]:
    errors: list[str] = []
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    verdict = data.get("verdict")
    if verdict not in ALLOWED_VERDICT:
        errors.append(f"verdict must be one of {sorted(ALLOWED_VERDICT)}")
    coverage = data.get("coverage") or []
    if not coverage:
        errors.append("coverage must list at least one requirement row")
    waivers = {w.get("requirement_id") for w in (data.get("waivers") or [])}
    for row in coverage:
        rid = row.get("requirement_id", "?")
        status = row.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"{rid}: status must be one of {sorted(ALLOWED_STATUS)}")
        if not row.get("evidence"):
            errors.append(f"{rid}: evidence link or reason is required")
        if status == "WAIVED" and rid not in waivers:
            errors.append(f"{rid}: WAIVED needs a matching waivers entry")
    for w in data.get("waivers") or []:
        if not w.get("justification") or not w.get("approval_ref"):
            errors.append(
                f"{w.get('requirement_id', '?')}: waiver needs justification and approval_ref"
            )
    if verdict == "VERIFIED":
        bad = [r.get("requirement_id") for r in coverage if r.get("status") != "VERIFIED"]
        if bad:
            errors.append(f"VERIFIED verdict with non-verified rows: {bad}")
    return errors


if __name__ == "__main__":
    errs = validate_record(sys.argv[1])
    if errs:
        print("\n".join(errs))
        raise SystemExit(1)
    print("record OK")
