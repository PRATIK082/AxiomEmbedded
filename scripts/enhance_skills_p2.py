"""Apply P2 patterns to all skills not yet deeply enhanced.

Adds: copyright-safe standards references, impact tiers, deviation management,
builder+reviewer pairing, three-zone autonomy. Skips already-enhanced skills.

Usage:
  python scripts/enhance_skills_p2.py --dry-run
  python scripts/enhance_skills_p2.py --apply
"""
from __future__ import annotations
import argparse
import os
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
sys.path.insert(0, ROOT)


def _is_enhanced(text: str) -> bool:
    return "## Impact tiers" in text or "## Impact Tiers" in text


def _get_standards(fm: dict) -> list[str]:
    ax = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
    stds = ax.get("standards", []) or ax.get("standard_ids", []) or []
    return [str(s) for s in stds if s]


def _enhance(sid: str, dry_run: bool = True) -> bool:
    path = os.path.join(SKILLS, sid, "SKILL.md")
    if not os.path.exists(path):
        return False
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return False
    if _is_enhanced(text):
        return False  # already enhanced

    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        return False
    ax = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
    stds = _get_standards(fm)
    maturity = ax.get("maturity", "experimental")
    title = fm.get("title", sid.replace("-", " ").title())

    # Build the P2 block
    std_table = ""
    if stds:
        std_table = "| Rule | Standard clause | Impact |\n|---|---|---|\n"
        for i, s in enumerate(stds, 1):
            std_table += f"| R{i} | {s} | MEDIUM |\n"
    else:
        std_table = "| Rule | Standard clause | Impact |\n|---|---|---|\n| R1 | (none declared) | LOW |\n"

    block = f"""
## Copyright-safe standards references

Identifiers and clause numbers only -- no normative text reproduced.

{std_table}

## Impact tiers

| Tier | Meaning |
|---|---|
| CRITICAL | Safety/security-critical; requires human approval and impact assessment |
| HIGH | Significant impact; requires review |
| MEDIUM | Moderate impact; standard review |
| LOW | Minor impact; routine review |

### Rule impact assignments

All rules in this skill default to MEDIUM unless marked CRITICAL or HIGH
in the rule ID -> clause map above.

## Deviation management

Any deviation must be recorded with: Rule ID, reason, file/location,
approver, and date. CRITICAL-rule deviations require safety-lead approval
and an impact assessment. Deviations are first-class artifacts, not comments.

## Builder + reviewer

This skill follows the builder + reviewer pattern: the builder produces the
artifact, the reviewer independently verifies it before acceptance. No
artifact is accepted without reviewer sign-off.

## Three-zone autonomy

- **Core / evidence zone** (AI no access, human accountable): certified artifacts,
  evidence records, safety-critical code.
- **Gray zone** (AI assistant + HITL): AI plans and drafts; human decides and approves.
- **Non-critical zone** (AI unrestricted): documentation, examples, scaffolding, low-risk refactors.
"""

    # Find insertion point: before "## References" or at end
    ref_idx = text.rfind("## References")
    if ref_idx == -1:
        ref_idx = len(text)
    else:
        ref_idx = text.rfind("\n", 0, ref_idx)

    new_text = text[:ref_idx] + "\n" + block + "\n" + text[ref_idx:]

    # Also remove the old skeleton sections if present
    # (the P0 script added these; replace with enhanced versions)
    old_sections = ["## Deviation management\n\nAny deviation from a rule or standard must be recorded with: Rule ID, reason,\nfile/location, approver, and date. Deviations are tracked as first-class\nartifacts, not comments. (Straion pattern.)\n",
                    "## Builder + reviewer\n\nThis skill follows the builder + reviewer pattern: the builder produces the\nartifact, the reviewer independently verifies it before acceptance. No\nartifact is accepted without reviewer sign-off.\n",
                    "## Three-zone autonomy\n\n- **Core / evidence zone** (AI no access, human accountable): certified artifacts,\n  evidence records, safety-critical code, release baselines. AI must not read or write here without an explicit human-approved change request.\n- **Gray zone** (AI assistant + HITL): AI plans the path and drafts changes, but a human decides and approves each step. Includes architecture, requirements, tests with safety impact, and configuration affecting verification.\n- **Non-critical zone** (AI unrestricted): documentation, examples, generated scaffolding, low-risk refactors, and tooling glue. AI may act autonomously, subject to review.\n",
                    "## Copyright-safe standards\n\nNever reproduce normative standards text. Store identifiers, clause numbers,\napplicability metadata, mappings, and project-authored interpretations only.\n"]

    for old in old_sections:
        new_text = new_text.replace(old, "")

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

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
        if not os.path.exists(os.path.join(SKILLS, sid, "SKILL.md")):
            continue
        if _enhance(sid, dry):
            count += 1
    print(f"mode={'dry-run' if dry else 'apply'}")
    print(f"skills enhanced: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
