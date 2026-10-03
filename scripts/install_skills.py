"""Install AxiomEmbedded skills into a host harness skills directory.

Each skills/<id>/ folder (SKILL.md with agent-skills frontmatter + manifest.yaml)
is copied as-is, which is the layout Claude Code, OpenCode, Codex, and
Antigravity all discover.

Usage:
    python scripts/install_skills.py --harness claude --dest .claude/skills
    python scripts/install_skills.py --harness opencode --dest .opencode/skills
    python scripts/install_skills.py --harness codex --dest .codex/skills
    python scripts/install_skills.py --harness antigravity --dest .antigravity/skills
    python scripts/install_skills.py --domain automotive --platform mcu --dest <dir>
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT))
from packages.skills.engage import engage  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", required=True, choices=["claude", "opencode", "codex", "antigravity"])
    ap.add_argument("--dest", required=True)
    ap.add_argument("--domain", default=None)
    ap.add_argument("--platform", default=None)
    args = ap.parse_args()

    selection = engage(args.domain, args.platform)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    for skill_id in selection["skills"]:
        src = REPO_ROOT / "skills" / skill_id
        shutil.copytree(src, dest / skill_id, dirs_exist_ok=True)
    print(f"[{args.harness}] installed {selection['skill_count']} skills -> {dest}")
    if selection["profiles"]:
        print(f"suggested profiles: {', '.join(selection['profiles'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
