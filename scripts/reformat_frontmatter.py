"""Reformat SKILL.md frontmatter to classic compact inline style (idempotent).

Arrays become inline [a, b]; descriptions use folded '>' block; blank lines
group axiom fields. Content is unchanged.
"""
from __future__ import annotations
import os, pathlib, re, textwrap, yaml

ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded")
SKILLS = ROOT / "skills"

def inline(items):
    if not isinstance(items, list):
        items = [items] if items is not None else []
    out = []
    for it in items:
        s = "" if it is None else str(it)
        if s == "":
            out.append('""')
            continue
        if any(c in s for c in ",[]{}#:&*!|>'\"%@`") or s != s.strip() or s.startswith(("-", "?", ":")):
            out.append('"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"')
        else:
            out.append(s)
    return "[" + ", ".join(out) + "]"

def wrap_desc(text, width=78):
    text = " ".join(str(text).split())
    if not text:
        return ""
    lines = textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    return "\n  ".join(lines)

def fmt_top(fm):
    lines = []
    # order
    if "name" in fm: lines.append(f"name: {fm['name']}")
    if "title" in fm: lines.append(f"title: {fm['title']}")
    # description
    desc = fm.get("description", "")
    if desc is not None:
        lines.append("description: >")
        lines.append("  " + wrap_desc(desc))
    if "version" in fm: lines.append(f"version: {fm['version']}")
    if "author" in fm: lines.append(f"author: {fm['author']}")
    if "license" in fm: lines.append(f"license: {fm['license']}")
    if "domains" in fm: lines.append(f"domains: {inline(fm['domains'])}")
    if "platforms" in fm: lines.append(f"platforms: {inline(fm['platforms'])}")
    return lines

def fmt_axiom(ax):
    lines = []
    order1 = ["dotted_name", "domain", "subdomain", "category", "maturity", "owner"]
    for k in order1:
        if k in ax and ax[k] is not None:
            v = ax[k]
            if isinstance(v, list):
                lines.append(f"  {k}: {inline(v)}")
            else:
                lines.append(f"  {k}: {v}")
    # tags
    if "tags" in ax:
        lines.append(f"  tags: {inline(ax.get('tags'))}")
    lines.append("")
    # related_skills, checklists
    if "related_skills" in ax:
        lines.append(f"  related_skills: {inline(ax.get('related_skills'))}")
    if "checklists" in ax:
        lines.append(f"  checklists: {inline(ax.get('checklists'))}")
    if "templates" in ax:
        lines.append(f"  templates: {inline(ax.get('templates'))}")
    if "scripts" in ax:
        lines.append(f"  scripts: {inline(ax.get('scripts'))}")
    lines.append("")
    # lifecycle group
    for k in ["lifecycle", "standards", "artifact_types", "mcp_tools"]:
        if k in ax:
            lines.append(f"  {k}: {inline(ax.get(k))}")
    lines.append("")
    # risk group
    for k in ["risk_level", "review_required", "safety_critical"]:
        if k in ax:
            v = ax[k]
            if isinstance(v, bool):
                v = "true" if v else "false"
            lines.append(f"  {k}: {v}")
    for k in ["inputs", "outputs", "required_tools", "optional_tools"]:
        if k in ax:
            lines.append(f"  {k}: {inline(ax.get(k))}")
    return lines

def reformat(sid):
    d = SKILLS / sid
    sf = d / "SKILL.md"
    txt = sf.read_text(encoding="utf-8")
    if not txt.startswith("---"):
        return False
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return False
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    # build new frontmatter
    new_lines = ["---"]
    new_lines += fmt_top(fm)
    new_lines.append("")
    new_lines.append("axiom:")
    ax = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
    new_lines += fmt_axiom(ax)
    # remove trailing empty lines before closing
    while new_lines and new_lines[-1] == "":
        new_lines.pop()
    new_lines.append("---")
    new_fm = "\n".join(new_lines) + "\n"
    new_text = new_fm + body.lstrip("\n")
    # validate parse
    try:
        yaml.safe_load(new_text.split("---", 2)[1])
    except Exception as e:
        raise RuntimeError(f"{sid}: YAML parse failed: {e}")
    sf.write_text(new_text, encoding="utf-8")
    return True

def main():
    n = 0
    for p in sorted(SKILLS.iterdir()):
        if not p.is_dir() or p.name.startswith(("_", ".")):
            continue
        if not (p / "SKILL.md").exists():
            continue
        reformat(p.name)
        n += 1
    print(f"reformatted {n} skills")

if __name__ == "__main__":
    main()
