"""Backfill contract fields (inputs/outputs/required_tools/optional_tools/artifact_types)
in SKILL.md frontmatter axiom block for skills missing them. Stdlib only, idempotent."""
from __future__ import annotations
import os
import pathlib
import re
import yaml

ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded")
SKILLS = ROOT / "skills"

DEFAULTS = {
    "inputs": ["project context", "applicable standards", "existing artifacts"],
    "outputs": ["engineering artifact", "review report"],
    "required_tools": [],
    "optional_tools": [],
    "artifact_types": ["report"],
    "mcp_tools": [],
    "standards": [],
    "lifecycle": ["discover", "plan", "implement", "verify", "evidence"],
}

def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parts[1], parts[2]

def main():
    changed = 0
    for p in sorted(SKILLS.iterdir()):
        if not p.is_dir() or p.name.startswith(("_", ".")):
            continue
        sf = p / "SKILL.md"
        if not sf.exists():
            continue
        text = sf.read_text(encoding="utf-8")
        fm_raw, body = split_frontmatter(text)
        if fm_raw is None:
            continue
        try:
            fm = yaml.safe_load(fm_raw) or {}
        except Exception:
            continue
        axiom = fm.get("axiom")
        if not isinstance(axiom, dict):
            axiom = {}
            fm["axiom"] = axiom
        modified = False
        for k, v in DEFAULTS.items():
            if k not in axiom or axiom.get(k) is None:
                axiom[k] = list(v) if isinstance(v, list) else v
                modified = True
        if not modified:
            continue
        # rewrite frontmatter preserving order-ish: dump full fm
        new_fm = yaml.safe_dump(fm, sort_keys=False, default_flow_style=False, allow_unicode=False)
        # safe_dump may produce '...' no; ensure trailing newline
        new_text = "---\n" + new_fm + "---\n" + body.lstrip("\n")
        # ensure single blank line after frontmatter
        if not new_text.startswith("---\n"):
            pass
        sf.write_text(new_text, encoding="utf-8")
        changed += 1
    print(f"backfilled {changed} skills")

if __name__ == "__main__":
    main()
