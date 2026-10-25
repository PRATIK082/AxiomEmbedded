"""Skill validator: whole-catalog validation (frontmatter, files, dupes, index linkage)."""
from __future__ import annotations
import json
import pathlib
import yaml

from packages.skills.loader import validate_skill_doc
from packages.skills.registry import load_catalog, check_catalog

from packages.paths import ROOT


def validate_all(catalog_path: pathlib.Path | None = None) -> dict:
    results: list[dict] = []
    skills_dir = ROOT / "skills"
    ids = sorted(p.name for p in skills_dir.iterdir()
                 if p.is_dir() and (p / "SKILL.md").exists()
                 and not p.name.startswith(("_", ".")))
    for sid in ids:
        results.append(validate_skill_doc(sid))
    catalog_report = None
    cp = pathlib.Path(catalog_path) if catalog_path else ROOT / "skills" / "catalog.yaml"
    if cp.exists():
        catalog_report = check_catalog(load_catalog(cp))
        cat_ids = {e["id"] for e in load_catalog(cp).get("skills", [])}
        missing = set(ids) - cat_ids - {"_templates"}
        if missing:
            catalog_report["warnings"].append(
                f"skills on disk missing from catalog: {sorted(missing)}")
    # index linkage
    try:
        index = json.loads((ROOT / "registries" / "skill-index.json").read_text(
            encoding="utf-8"))
        unindexed = set(ids) - set(index.get("skills", {}))
    except FileNotFoundError:
        unindexed = set(ids)
    ok = all(r["valid"] for r in results) and (
        catalog_report is None or catalog_report["valid"])
    return {"valid": ok, "skills": results,
            "catalog": catalog_report,
            "unindexed_in_skill_index": sorted(unindexed)}
