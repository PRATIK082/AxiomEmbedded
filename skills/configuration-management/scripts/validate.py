"""Validation script for configuration-management (stdlib only).

Run: python scripts/validate.py [artifact_dir]
"""
from __future__ import annotations
import json
import pathlib
import sys


def main() -> int:
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    errors = []
    # Skill-specific checks are added during content refinement.
    # Generic structural checks:
    skill_dir = pathlib.Path(__file__).resolve().parents[1]
    if not (skill_dir / "SKILL.md").exists():
        errors.append("SKILL.md missing")
    if not (skill_dir / "manifest.yaml").exists():
        errors.append("manifest.yaml missing")
    if not (skill_dir / "checklists").is_dir():
        errors.append("checklists/ missing")
    # validate evals.json if present
    evals = skill_dir / "tests" / "evals.json"
    if evals.exists():
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
            if not isinstance(data.get("scenarios"), list) or len(data["scenarios"]) < 1:
                errors.append("evals.json must contain >=1 scenario")
        except Exception as exc:
            errors.append(f"evals.json parse error: {exc}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
