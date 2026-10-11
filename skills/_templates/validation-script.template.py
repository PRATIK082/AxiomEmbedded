"""Validation script template (stdlib only). Copy to skills/<id>/scripts/validate.py."""
from __future__ import annotations
import pathlib
import sys


def main() -> int:
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    errors = []
    # TODO: add deterministic checks for this skill's artifacts
    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
