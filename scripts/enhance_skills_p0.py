"""Apply P0 universal patterns to all skills that lack them.

Patterns from deep research (ADOPTION_PLAN.md P0):
- Impact tiers (CRITICAL/HIGH/MEDIUM/LOW) for rules
- Copyright-safe standards references
- Deviation management section
- Builder + reviewer pairing note
- Three-zone autonomy note

Usage:
  python scripts/enhance_skills_p0.py --dry-run   # report only
  python scripts/enhance_skills_p0.py --apply     # write files
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


def _has_section(text: str, heading: str) -> bool:
    return heading.lower() in text.lower()


def _get_axiom(fm: dict) -> dict:
    return fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}


def _enhance_skill(sid: str, dry_run: bool = True) -> list[str]:
    """Returns list of changes made (or would be made)."""
    path = os.path.join(SKILLS, sid, "SKILL.md")
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        return []
    ax = _get_axiom(fm)
    changes = []

    # Check if already enhanced (has deviation management section)
    if "## Deviation management" in text or "## Deviation Management" in text:
        return []  # already enhanced

    # Find insertion point: before "## References" or at end
    ref_idx = text.rfind("## References")
    if ref_idx == -1:
        ref_idx = len(text)
    else:
        # find the line before ## References
        ref_idx = text.rfind("\n", 0, ref_idx)

    additions = []

    # 1. Deviation management section
    if "## Deviation" not in text:
        additions.append("""
## Deviation management

Any deviation from a rule or standard must be recorded with: Rule ID, reason,
file/location, approver, and date. Deviations are tracked as first-class
artifacts, not comments. (Straion pattern.)
""")
        changes.append("deviation-management")

    # 2. Builder + reviewer pairing
    if "## Builder" not in text and "builder" not in text.lower().split("## references")[0][-200:]:
        additions.append("""
## Builder + reviewer

This skill follows the builder + reviewer pattern: the builder produces the
artifact, the reviewer independently verifies it before acceptance. No
artifact is accepted without reviewer sign-off.
""")
        changes.append("builder-reviewer")

    # 3. Three-zone autonomy
    if "three-zone" not in text.lower() and "core / evidence zone" not in text.lower():
        additions.append("""
## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code. AI must not modify without human approval.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.
""")
        changes.append("three-zone-autonomy")

    # 4. Copyright-safe standards
    if "copyright-safe" not in text.lower() and "normative" not in text.lower():
        additions.append("""
## Copyright-safe standards

Never reproduce normative standards text. Store identifiers, clause numbers,
applicability metadata, mappings, and project-authored interpretations only.
""")
        changes.append("copyright-safe")

    if not additions:
        return []

    addition_text = "\n".join(additions)
    new_text = text[:ref_idx] + "\n" + addition_text + "\n" + text[ref_idx:]

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

    return changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = not args.apply
    total_changes = 0
    skills_changed = 0
    for sid in sorted(os.listdir(SKILLS)):
        if sid.startswith("_") or not os.path.isdir(os.path.join(SKILLS, sid)):
            continue
        if not os.path.exists(os.path.join(SKILLS, sid, "SKILL.md")):
            continue
        changes = _enhance_skill(sid, dry)
        if changes:
            skills_changed += 1
            total_changes += len(changes)
            if not dry:
                pass
    print(f"mode={'dry-run' if dry else 'apply'}")
    print(f"skills enhanced: {skills_changed}")
    print(f"total changes: {total_changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
