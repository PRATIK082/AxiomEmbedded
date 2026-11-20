"""Validate a axiom-behavior-tree-spec-review artifact. Stdlib only."""
from __future__ import annotations
import pathlib
import sys
import re


REQUIRED_SECTIONS = ['Deliverables', 'Acceptance Criteria', 'Acceptance']
REQUIRED_STANDARDS = []
ARTIFACT_TYPES = ['behavior-tree spec', 'node contract table']


def validate(path: str) -> list[str]:
    """Return list of error strings; empty means OK."""
    errors = []
    p = pathlib.Path(path)
    if not p.exists():
        errors.append(f"file not found: {path}")
        return errors
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        errors.append("record is empty")
        return errors
    if "TODO" in text:
        errors.append("record contains unreplaced TODO markers")
    # Check required sections
    for section in REQUIRED_SECTIONS:
        if section.lower() not in text.lower():
            errors.append(f"missing required section: {section}")
    # Check standards references
    for std in REQUIRED_STANDARDS:
        if std and std.lower() not in text.lower():
            errors.append(f"missing standards reference: {std}")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate.py <artifact-path>")
        return 2
    errs = validate(sys.argv[1])
    if errs:
        for e in errs:
            print(f"ERROR: {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
