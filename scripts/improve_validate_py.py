"""Improve validate.py stubs with skill-specific checks based on frontmatter.

Reads each skill's SKILL.md, extracts artifact_types, standards, deliverables,
and generates a richer validate.py that checks for those specific elements.

Usage:
  python scripts/improve_validate_py.py --dry-run
  python scripts/improve_validate_py.py --apply
"""
from __future__ import annotations
import argparse
import os
import re
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
sys.path.insert(0, ROOT)

VALIDATE_PY_TEMPLATE = '''"""Validate a {sid} artifact. Stdlib only."""
from __future__ import annotations
import pathlib
import sys
import re


REQUIRED_SECTIONS = {sections}
REQUIRED_STANDARDS = {standards}
ARTIFACT_TYPES = {artifact_types}


def validate(path: str) -> list[str]:
    """Return list of error strings; empty means OK."""
    errors = []
    p = pathlib.Path(path)
    if not p.exists():
        errors.append(f"file not found: {{path}}")
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
            errors.append(f"missing required section: {{section}}")
    # Check standards references
    for std in REQUIRED_STANDARDS:
        if std and std.lower() not in text.lower():
            errors.append(f"missing standards reference: {{std}}")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate.py <artifact-path>")
        return 2
    errs = validate(sys.argv[1])
    if errs:
        for e in errs:
            print(f"ERROR: {{e}}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _extract_sections(text: str) -> list[str]:
    """Extract section headings from SKILL.md body."""
    sections = []
    for line in text.splitlines():
        if line.startswith("## "):
            sections.append(line.strip("# ").strip())
    # Filter to relevant artifact sections
    relevant = [s for s in sections if any(k in s.lower() for k in
                ["deliverable", "acceptance", "verification", "evidence", "output"])]
    return relevant[:5] if relevant else ["Deliverables", "Acceptance Criteria"]


def _extract_standards(fm: dict) -> list[str]:
    ax = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
    stds = ax.get("standards", []) or ax.get("standard_ids", []) or []
    return [str(s) for s in stds if s]


def _extract_artifact_types(fm: dict) -> list[str]:
    ax = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
    return list(ax.get("artifact_types", []) or [])


def improve(sid: str, dry_run: bool = True) -> bool:
    path = os.path.join(SKILLS, sid, "SKILL.md")
    if not os.path.exists(path):
        return False
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        return False

    sections = _extract_sections(text)
    standards = _extract_standards(fm)
    artifact_types = _extract_artifact_types(fm)

    new_content = VALIDATE_PY_TEMPLATE.format(
        sid=sid,
        sections=repr(sections),
        standards=repr(standards),
        artifact_types=repr(artifact_types),
    )

    vp = os.path.join(SKILLS, sid, "scripts", "validate.py")
    if not os.path.exists(vp):
        return False

    current = open(vp, encoding="utf-8").read()
    # Only replace if current is a stub (no REQUIRED_SECTIONS)
    if "REQUIRED_SECTIONS" in current:
        return False  # already improved

    if not dry_run:
        with open(vp, "w", encoding="utf-8") as f:
            f.write(new_content)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = not args.apply
    count = 0
    for sid in sorted(os.listdir(SKILLS)):
        if sid.startswith("_") or not os.path.isdir(os.path.join(SKILLS, sid)):
            continue
        if improve(sid, dry):
            count += 1
    print(f"mode={'dry-run' if dry else 'apply'}")
    print(f"skills improved: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
