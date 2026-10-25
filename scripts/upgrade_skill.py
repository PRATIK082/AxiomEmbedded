"""Upgrade a skill scaffold to beta maturity by adding a checker script stub.

Usage:
    python scripts/upgrade_skill.py <skill-id> [--apply]
Dry-run by default. Only flips maturity when a checker script exists.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def upgrade(skill_id: str, apply: bool = False) -> dict:
    d = SKILLS / skill_id
    if not (d / "SKILL.md").exists():
        return {"skill": skill_id, "status": "error", "message": "SKILL.md not found"}
    fm_path = d / "SKILL.md"
    text = fm_path.read_text(encoding="utf-8")
    # ensure scripts dir
    scripts = d / "scripts"
    checker = scripts / f"check_{skill_id.replace('axiom-', '').replace('-', '_')}.py"
    created_checker = False
    if not checker.exists():
        scripts.mkdir(exist_ok=True)
        checker.write_text(
            '"""Checker stub for {sid}. Replace with real deterministic checks."""\n'
            "from __future__ import annotations\nimport sys\n\n"
            "def main() -> int:\n    print(\"{sid}: scaffold checker (implement real checks)\")\n    return 0\n\n"
            'if __name__ == "__main__":\n    raise SystemExit(main())\n'.format(sid=skill_id),
            encoding="utf-8",
        )
        created_checker = True
    # flip maturity in frontmatter if present
    new_text = text
    if "maturity: experimental" in text:
        new_text = text.replace("maturity: experimental", "maturity: beta", 1)
    changed = new_text != text
    if apply:
        if changed:
            fm_path.write_text(new_text, encoding="utf-8")
        # register checker in frontmatter axiom.checklists? leave as scripts only
    return {"skill": skill_id, "status": "ok", "checker": str(checker.relative_to(ROOT)),
            "created_checker": created_checker, "maturity_flipped": changed, "applied": apply}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_id")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    print(upgrade(args.skill_id, args.apply))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
