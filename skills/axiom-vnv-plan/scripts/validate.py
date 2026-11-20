"""Validate a axiom-vnv-plan artifact. Stdlib only."""
from __future__ import annotations
import pathlib
import sys
import re


REQUIRED_SECTIONS = ['Acceptance']
REQUIRED_STANDARDS = ['ISO 12100:2010', 'ISO 13849-2:2012', 'ISO/TS 15066:2016', 'IEC 62061:2021']
ARTIFACT_TYPES = ['V&V plan', 'traceability matrix']


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
