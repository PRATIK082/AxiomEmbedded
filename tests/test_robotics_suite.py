"""Tests for the 38-pair robotics/industrial skill suite (builder + reviewer)."""
from __future__ import annotations
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

CATEGORIES = {"assessment", "compliance", "design", "verification",
              "procedure", "documentation"}
DOMAINS = {"robotics", "industrial"}

FAMILY_OF = {
    "ANSI/RIA R15.06": "ansi-r15-06",
    "ISO 10218": "iso-10218", "ISO 12100": "iso-12100",
    "ISO 13849": "iso-13849", "ISO 13850": "iso-13850",
    "ISO 14118": "iso-14118", "ISO 11161": "iso-11161",
    "ISO/TS 15066": "iso-ts-15066", "ISO 3691-4": "iso-3691-4",
    "ISO 9283": "iso-9283", "IEC 62061": "iec-62061",
    "IEC 61508": "iec-61508", "IEC 62443": "iec-62443",
    "IEC 62657": "iec-62657", "ANSI Z244.1": "ansi-z244",
    "EU 2023/1230": "eu-2023-1230", "ISO/IEC 23894": "iso-iec-23894",
    "ISO/IEC 23053": "iso-iec-23053",
}


def _suite_ids() -> list[str]:
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    return [e["id"] for e in cat["skills"]
            if (ROOT / "skills" / e["id"] / "references" / "standard-map.md").exists()
            and e["id"].startswith("axiom-")
            and (ROOT / "skills" / e["id"] / "SKILL.md").read_text(
                encoding="utf-8").find("scaffold_robotics_suite") >= 0]


def test_suite_pairs_symmetric():
    from packages.skills.loader import parse_skill_doc
    ids = set(_suite_ids())
    assert len(ids) == 76, len(ids)
    for sid in sorted(ids):
        fm, _ = parse_skill_doc(
            (ROOT / "skills" / sid / "SKILL.md").read_text(encoding="utf-8"))
        partner = (sid[:-len("-review")] if sid.endswith("-review")
                   else sid + "-review")
        assert partner in ids, (sid, "partner missing")
        assert partner in (fm["axiom"].get("related_skills") or []), (sid, "link")
        ax = fm["axiom"]
        assert ax["category"] in CATEGORIES, (sid, ax["category"])
        assert list(fm["domains"]) == [ax["domain"]] and ax["domain"] in DOMAINS, sid
        assert ax["maturity"] == "beta", sid
        assert ax["review_required"] is True, sid


def test_suite_standard_maps_cover_declared_standards():
    import re
    from packages.skills.loader import parse_skill_doc
    for sid in sorted(_suite_ids()):
        fm, _ = parse_skill_doc(
            (ROOT / "skills" / sid / "SKILL.md").read_text(encoding="utf-8"))
        stds = list(fm["axiom"].get("standards") or [])
        body = (ROOT / "skills" / sid / "references" / "standard-map.md").read_text(
            encoding="utf-8")
        for std in stds:
            base = std.split(":")[0]
            assert base in body, (sid, std)
            key = re.sub(r"-\d{4}$", "", base)
            family = FAMILY_OF.get(key)
            while family is None and "-" in key:
                key = key.rsplit("-", 1)[0]
                family = FAMILY_OF.get(key)
            assert family, (sid, std)
            assert (ROOT / "standards" / "industrial" / f"{family}.yaml").exists(), (sid, std)


def test_suite_docs_validate():
    from packages.skills.loader import validate_skill_doc
    bad = []
    for sid in sorted(_suite_ids()):
        rep = validate_skill_doc(sid)
        if not rep["valid"]:
            bad.append((sid, rep["errors"]))
    assert not bad, bad


def test_suite_registered_in_registry():
    reg = yaml.safe_load((ROOT / "skills" / "registry.yaml").read_text(encoding="utf-8"))
    paths = {s["path"] for s in reg["skills"]}
    missing = [sid for sid in _suite_ids() if f"skills/{sid}" not in paths]
    assert not missing, missing
