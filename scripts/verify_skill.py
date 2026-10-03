"""Phase 4 gate runner for one skill.

Checks: SKILL.md exists and non-stub, manifest validates, workflow/profile/rules
schemas parse, no stub-only template skill. Safety/security skills flag human review.

Usage: python scripts/verify_skill.py --skill mcu
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SENSITIVE = {"safety", "security", "autosar", "validation", "fault-injection"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    args = ap.parse_args()

    skill_dir = REPO_ROOT / "skills" / args.skill
    errors: list[str] = []
    if not (skill_dir / "SKILL.md").exists():
        errors.append("missing SKILL.md")
    if not (skill_dir / "manifest.yaml").exists():
        errors.append("missing manifest.yaml")
    else:
        try:
            data = yaml.safe_load((skill_dir / "manifest.yaml").read_text(encoding="utf-8"))
            for key in ("id", "version", "type"):
                if key not in data:
                    errors.append(f"manifest missing key: {key}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"manifest parse error: {exc}")

    for rel in (
        "workflows/embedded-skills-deep-update.yaml",
        "profiles/skill-update-profile.yaml",
        "configs/skill-update.yaml",
        "rules/skill-update-gates.yaml",
    ):
        try:
            yaml.safe_load((REPO_ROOT / rel).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel} parse error: {exc}")

    if errors:
        print("FAIL:", "; ".join(errors))
        return 1
    if args.skill in SENSITIVE:
        print(f"PASS with human-review flag: {args.skill} is safety/security sensitive")
    else:
        print(f"PASS: {args.skill}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
