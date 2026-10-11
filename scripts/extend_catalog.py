"""One-shot: add legacy (non-axiom-*) skills to catalog.yaml as production entries.

Keeps catalog.yaml = every skill (prompt1 rule). Rerunnable/idempotent.
"""
from __future__ import annotations
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    cat_p = ROOT / "skills" / "catalog.yaml"
    cat = yaml.safe_load(cat_p.read_text(encoding="utf-8"))
    have = {e["id"] for e in cat["skills"]}
    added = 0
    for d in sorted((ROOT / "skills").iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue
        if not (d / "SKILL.md").exists() or d.name in have:
            continue
        fm = yaml.safe_load(
            (d / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]) or {}
        doms = fm.get("domains", ["all"])
        cat["skills"].append({
            "id": d.name,
            "name": "axiom.legacy." + d.name,
            "title": str(fm.get("title", fm.get("name", d.name))),
            "version": str(fm.get("version", "1.0.0")),
            "domain": (doms[0] if doms else "all"),
            "subdomain": "legacy",
            "category": "legacy",
            "maturity": "production",
            "owner": "axiom-embedded",
            "tags": ["legacy"],
            "inputs": ["repository path", "objective"],
            "outputs": ["report"],
            "dependencies": [],
            "related_skills": [],
            "path": "skills/" + d.name,
            "enabled": True,
        })
        added += 1
    cat["skills"].sort(key=lambda e: e["id"])
    cat_p.write_text(yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")
    print(f"catalog: +{added} legacy entries ({len(cat['skills'])} total)")
    # keep registry.yaml covering every catalog skill
    reg_p = ROOT / "skills" / "registry.yaml"
    reg = yaml.safe_load(reg_p.read_text(encoding="utf-8"))
    have_paths = {s["path"] for s in reg["skills"]}
    for e in cat["skills"]:
        if e["path"] not in have_paths:
            reg["skills"].append({"name": e["name"], "path": e["path"],
                                  "domain": e["domain"],
                                  "maturity": e["maturity"]})
    reg["skills"].sort(key=lambda s: s["path"])
    reg_p.write_text(yaml.safe_dump(reg, sort_keys=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
