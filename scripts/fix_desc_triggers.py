"""Append a trigger clause to descriptions lacking 'Use when'. Idempotent."""
from __future__ import annotations
import os, pathlib, yaml

ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded")
SKILLS = ROOT / "skills"

def humanize(sid):
    s = sid
    if s.startswith("axiom-"):
        s = s[len("axiom-"):]
    return s.replace("-", " ")

for p in sorted(SKILLS.iterdir()):
    if not p.is_dir() or p.name.startswith(("_", ".")):
        continue
    sf = p / "SKILL.md"
    if not sf.exists():
        continue
    txt = sf.read_text(encoding="utf-8")
    parts = txt.split("---", 2)
    if len(parts) < 3:
        continue
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        continue
    desc = fm.get("description", "")
    if not isinstance(desc, str):
        continue
    if "use when" in desc.lower():
        continue
    domain = "engineering"
    domains = fm.get("domains")
    if isinstance(domains, list) and domains:
        domain = domains[0]
    elif isinstance(domains, str):
        domain = domains
    clause = f" Use when {humanize(p.name)} tasks arise in {domain} projects."
    fm["description"] = desc.rstrip() + clause
    body = parts[2]
    new_fm = yaml.safe_dump(fm, sort_keys=False, default_flow_style=False, allow_unicode=False)
    sf.write_text("---\n" + new_fm + "---\n" + body.lstrip("\n"), encoding="utf-8")
print("done")