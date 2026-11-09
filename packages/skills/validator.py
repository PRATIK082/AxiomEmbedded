"""Skill validator: whole-catalog validation (frontmatter, files, dupes, index linkage)."""
from __future__ import annotations
import json
import pathlib
import yaml

from packages.skills.loader import validate_skill_doc, load_skill
from packages.skills.registry import load_catalog, check_catalog
import yaml as _yaml

from packages.paths import ROOT


def validate_all(catalog_path: pathlib.Path | None = None) -> dict:
    results: list[dict] = []
    skills_dir = ROOT / "skills"
    ids = sorted(p.name for p in skills_dir.iterdir()
                 if p.is_dir() and (p / "SKILL.md").exists()
                 and not p.name.startswith(("_", ".")))
    for sid in ids:
        r = validate_skill_doc(sid)
        # manifest.yaml validation
        merrs = []
        mp = skills_dir / sid / "manifest.yaml"
        if not mp.exists():
            merrs.append("manifest.yaml missing")
        else:
            try:
                man = _yaml.safe_load(mp.read_text(encoding="utf-8")) or {}
            except Exception as exc:
                man = {}
                merrs.append(f"manifest.yaml parse error: {exc}")
            if man:
                if man.get("id") and man.get("id") != sid:
                    merrs.append(f"manifest id {man.get('id')!r} != {sid!r}")
                if man.get("version") and man.get("version") != r and False:
                    pass
                # version parity with SKILL.md frontmatter
                try:
                    fm_ver = load_skill(sid)["frontmatter"].get("version")
                    if man.get("version") and fm_ver and man.get("version") != fm_ver:
                        merrs.append(f"manifest version {man.get('version')!r} != SKILL.md {fm_ver!r}")
                except Exception:
                    pass
                if not man.get("contract_version"):
                    merrs.append("manifest missing contract_version")
        if merrs:
            r["errors"] = r["errors"] + [f"manifest: {e}" for e in merrs]
            r["valid"] = False
        results.append(r)
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
