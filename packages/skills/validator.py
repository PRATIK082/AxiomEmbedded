"""Skill validator: whole-catalog validation (frontmatter, files, dupes, index linkage)."""
from __future__ import annotations
import json
import pathlib
import yaml

from packages.skills.loader import validate_skill_doc, load_skill
from packages.skills.registry import load_catalog, check_catalog
import yaml as _yaml

from packages.paths import ROOT


_DESA_CACHE: dict = {}


def _desa_taxonomies() -> dict:
    if _DESA_CACHE.get("ok"):
        return _DESA_CACHE
    try:
        acts = yaml.safe_load((ROOT / "taxonomies" / "activities.yaml").read_text(encoding="utf-8")) or {}
        kinds = yaml.safe_load((ROOT / "taxonomies" / "skill-types.yaml").read_text(encoding="utf-8")) or {}
        regs = yaml.safe_load((ROOT / "standards" / "registry.yaml").read_text(encoding="utf-8")) or {}
    except Exception:
        _DESA_CACHE["ok"] = True
        _DESA_CACHE["activities"] = set()
        _DESA_CACHE["kinds"] = set()
        _DESA_CACHE["standards"] = {}
        return _DESA_CACHE
    _DESA_CACHE["activities"] = set((acts.get("activities") or {}).keys())
    _DESA_CACHE["kinds"] = set((kinds.get("capability_kinds") or {}).keys())
    stds = {}
    for s in regs.get("standards", []) or []:
        stds[str(s.get("id"))] = str(s.get("status", "published"))
    _DESA_CACHE["standards"] = stds
    _DESA_CACHE["ok"] = True
    return _DESA_CACHE


def desa_checks(skill_id: str, axiom: dict) -> tuple[list, list]:
    """Phase 2/6 DESA checks: activity, kind, standards lifecycle. Non-blocking warnings."""
    errs: list[str] = []
    warns: list[str] = []
    if not axiom:
        return errs, warns
    tax = _desa_taxonomies()
    acts = tax.get("activities", set())
    kinds = tax.get("kinds", set())
    stds = tax.get("standards", {})
    act = axiom.get("activity", "")
    if act and acts and act not in acts:
        warns.append(f"desa: unknown activity {act!r}")
    kind = axiom.get("capability_kind", axiom.get("capability-kind", axiom.get("type", "")))
    if kind and kinds and kind not in kinds:
        warns.append(f"desa: unknown capability_kind {kind!r}")
    for sid in axiom.get("standard_ids", axiom.get("standards", [])) or []:
        key = str(sid).lower().replace(" ", "-").split(":")[0]
        # normalize common display forms e.g. "ISO 26262:2018" -> iso-26262
        aliases = {
            "iso-26262": "iso-26262", "iso26262": "iso-26262",
            "iso-sae-21434": "iso-sae-21434", "iso21434": "iso-sae-21434",
            "automotive-spice": "automotive-spice", "aspice": "automotive-spice",
            "misra-c": "misra-c", "misra-cpp": "misra-cpp",
        }
        norm = aliases.get(key, key)
        if stds and norm not in stds:
            warns.append(f"desa: standard {sid!r} not in standards/registry.yaml")
        elif stds.get(norm) in ("draft", "pre-release", "proposed"):
            warns.append(f"desa: standard {sid!r} is {stds.get(norm)}; must not replace published edition")
    return errs, warns


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

        # Production-grade structural checks
        fm = {}
        try:
            fm = load_skill(sid)["frontmatter"] or {}
        except Exception:
            fm = {}
        axiom = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
        maturity = axiom.get("maturity", "experimental")
        strict = maturity in ("beta", "production")
        sdir = skills_dir / sid
        def _has(sub):
            p = sdir / sub
            return p.is_dir() and any(p.iterdir())
        pg_errors = []
        pg_warnings = []
        if not _has("tests"):
            (pg_errors if strict else pg_warnings).append("tests/ missing or empty")
        if not (sdir / "scripts" / "validate.py").exists():
            (pg_errors if strict else pg_warnings).append("scripts/validate.py missing")
        if not _has("references"):
            (pg_errors if strict else pg_warnings).append("references/ missing or empty")
        if not _has("checklists"):
            (pg_errors if strict else pg_warnings).append("checklists/ missing or empty")
        if not _has("templates"):
            pg_warnings.append("templates/ missing or empty")
        desc = fm.get("description", "") or ""
        if len(desc) < 40:
            (pg_errors if strict else pg_warnings).append(f"description too short ({len(desc)} < 40)")
        if len(desc) > 1024:
            pg_warnings.append(f"description too long ({len(desc)} > 1024)")
        low = desc.lower()
        if low.startswith(("helps", "does ", "processes data", "utility", "tool for")):
            pg_warnings.append("vague description opener")
        # progressive disclosure
        try:
            lines = (sdir / "SKILL.md").read_text(encoding="utf-8").splitlines()
            if len(lines) > 500:
                pg_warnings.append(f"SKILL.md {len(lines)} lines (>500)")
        except Exception:
            pass
        if pg_errors:
            r["errors"] = r["errors"] + [f"prod-grade: {e}" for e in pg_errors]
            r["valid"] = False
        if pg_warnings:
            r["warnings"] = r.get("warnings", []) + [f"prod-grade: {w}" for w in pg_warnings]
        try:
            _derr, _dwarn = desa_checks(sid, axiom)
            if _derr:
                r["errors"] = r["errors"] + _derr
                r["valid"] = False
            if _dwarn:
                r["warnings"] = r.get("warnings", []) + _dwarn
        except Exception:
            pass
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
