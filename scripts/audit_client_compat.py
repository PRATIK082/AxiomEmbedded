"""Audit: OpenClaw/Hermes skill compatibility across the catalog."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.skills.loader import parse_skill_doc  # noqa: E402


def main() -> int:
    bad = []
    total = 0
    for d in sorted((ROOT / "skills").iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        f = d / "SKILL.md"
        if not f.exists():
            bad.append((d.name, "missing SKILL.md"))
            continue
        total += 1
        try:
            fm, _ = parse_skill_doc(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            bad.append((d.name, f"frontmatter parse: {e}"))
            continue
        name = str(fm.get("name", ""))
        desc = str(fm.get("description", "")).strip()
        if name != d.name:
            bad.append((d.name, f"name mismatch: {name!r}"))
        if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            bad.append((d.name, f"name not claw-slug: {name!r}"))
        if not desc:
            bad.append((d.name, "empty description"))
    print(f"checked={total} problems={len(bad)}")
    for sid, why in bad[:30]:
        print(f"  {sid}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
