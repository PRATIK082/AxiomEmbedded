"""Assurance slice tests: envelope validation, traceability, reviews, example chain."""
from __future__ import annotations
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "industrial-robot-cell" / "artifacts"
REVIEWS = ROOT / "examples" / "industrial-robot-cell" / "reviews"
NEW_SKILLS = ["axiom-scope-context", "axiom-scope-context-review", "axiom-hazard-risk",
              "axiom-hazard-risk-review", "axiom-safety-requirements",
              "axiom-safety-requirements-review", "axiom-vnv-plan",
              "axiom-vnv-plan-review", "axiom-threat-model", "axiom-threat-model-review"]


def test_new_skills_validate():
    from packages.skills.loader import validate_skill_doc
    for sid in NEW_SKILLS:
        rep = validate_skill_doc(sid)
        assert rep["valid"], (sid, rep["errors"])


def test_example_artifacts_validate():
    from packages.skills.assurance import validate_artifact_file
    files = sorted(EXAMPLE.glob("*.yaml"))
    assert len(files) == 5
    for f in files:
        rep = validate_artifact_file(f)
        assert rep["valid"], (f.name, rep["errors"])


def test_example_reviews_validate():
    from packages.skills.assurance import validate_artifact_file
    files = sorted(REVIEWS.glob("*.yaml"))
    assert len(files) == 5
    for f in files:
        rep = validate_artifact_file(f)
        assert rep["valid"], (f.name, rep["errors"])
        assert rep["kind"] == "review-report"


def test_traceability_passes():
    from packages.skills.assurance import check_traceability
    rep = check_traceability(EXAMPLE)
    assert rep["valid"], rep["errors"]
    assert rep["counts"] == {"requirements": 5, "hazards": 4, "tests": 5,
                             "threats": 2, "artifacts": 5}


def test_traceability_flags_orphan():
    from packages.skills.assurance import validate_artifact, check_traceability
    import tempfile
    bad = {"artifact_id": "T1", "schema_version": "1.0.0", "kind": "safety-requirements",
           "status": "draft", "domain": "industrial", "created_at": "2026-10-17T00:00:00Z",
           "updated_at": "2026-10-17T00:00:00Z", "author": "t", "approval_status": "draft",
           "requirements": [{"id": "REQ-900", "text": "Orphan requirement.", "covers_hazards": [],
                              "verification": "test", "status": "draft"}]}
    assert not validate_artifact(bad)
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "req.yaml"
        import yaml
        p.write_text(yaml.safe_dump(bad), encoding="utf-8")
        rep = check_traceability(tmp)
        assert not rep["valid"]
        assert any("orphan requirement REQ-900" in e for e in rep["errors"])


def test_blocker_forces_resubmit_verdict():
    from packages.skills.assurance import build_review, validate_artifact
    report = build_review("X-01", [{"id": "REV-001", "severity": "Blocker",
                                    "location": "threats", "evidence": "none",
                                    "recommendation": "fix", "owner": "team"}])
    assert report["verdict"] == "revise-and-resubmit"
    assert not validate_artifact(report)
    clean = build_review("X-01", [])
    assert clean["verdict"] == "accept"


def test_review_is_separate_from_target(tmp_path):
    from packages.skills.assurance import load_doc
    target = load_doc(EXAMPLE / "threat-model.yaml")
    before = dict(target)
    review = load_doc(REVIEWS / "threat-review.yaml")
    assert review["target_artifact"] == "SEC-CELL-01"
    assert load_doc(EXAMPLE / "threat-model.yaml") == before


EXPECTED_STANDARDS = {
    "axiom-scope-context": ["ISO 12100:2010", "ISO 10218-2:2011", "ISO 11161:2007"],
    "axiom-scope-context-review": ["ISO 12100:2010", "ISO 10218-2:2011", "ISO 11161:2007"],
    "axiom-hazard-risk": ["ISO 12100:2010", "ISO 10218-1:2011", "ISO 10218-2:2011",
                          "ISO/TS 15066:2016", "ISO 13849-1:2023", "ISO 13850:2015",
                          "ISO 14118:2017"],
    "axiom-hazard-risk-review": ["ISO 12100:2010", "ISO 10218-1:2011", "ISO 10218-2:2011",
                                 "ISO/TS 15066:2016", "ISO 13849-1:2023", "ISO 13850:2015",
                                 "ISO 14118:2017"],
    "axiom-safety-requirements": ["ISO 12100:2010", "ISO 13849-1:2023", "ISO 13850:2015",
                                  "ISO 14118:2017", "IEC 62061:2021", "IEC 61508:2010"],
    "axiom-safety-requirements-review": ["ISO 12100:2010", "ISO 13849-1:2023", "ISO 13850:2015",
                                         "ISO 14118:2017", "IEC 62061:2021", "IEC 61508:2010"],
    "axiom-vnv-plan": ["ISO 12100:2010", "ISO 13849-2:2012", "ISO/TS 15066:2016",
                       "IEC 62061:2021"],
    "axiom-vnv-plan-review": ["ISO 12100:2010", "ISO 13849-2:2012", "ISO/TS 15066:2016",
                              "IEC 62061:2021"],
    "axiom-threat-model": ["IEC 62443-3-3:2013", "IEC 62443-3-2:2020",
                           "IEC 62443-4-1:2018", "IEC 62443-4-2:2019"],
    "axiom-threat-model-review": ["IEC 62443-3-3:2013", "IEC 62443-3-2:2020",
                                  "IEC 62443-4-1:2018", "IEC 62443-4-2:2019"],
}

STANDARD_FAMILIES = {
    "ISO 12100": "iso-12100", "ISO 10218": "iso-10218", "ISO/TS 15066": "iso-ts-15066",
    "ISO 13849": "iso-13849", "ISO 13850": "iso-13850", "ISO 14118": "iso-14118",
    "ISO 11161": "iso-11161", "IEC 62061": "iec-62061", "IEC 61508": "iec-61508",
    "IEC 62443": "iec-62443",
}

DEPENDENT_LINKS = {
    "axiom-scope-context": "axiom-robotics-system-integration",
    "axiom-hazard-risk": "axiom-functional-safety",
    "axiom-safety-requirements": "safety",
    "axiom-vnv-plan": "axiom-industrial-control-review",
    "axiom-threat-model": "security",
}


def _family_of(standard: str) -> str:
    base = standard.split(":")[0]
    for prefix, family in STANDARD_FAMILIES.items():
        if base == prefix or base.startswith(prefix + "-"):
            return family
    raise AssertionError(f"no registered family for {standard}")


def test_assurance_standards_declared_everywhere():
    import yaml
    from packages.skills.loader import parse_skill_doc
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    idx = {e["id"]: e for e in cat["skills"]}
    for sid, expected in EXPECTED_STANDARDS.items():
        entry = idx[sid]
        assert entry["standards"] == expected, (sid, "catalog")
        fm, _ = parse_skill_doc(
            (ROOT / entry["path"] / "SKILL.md").read_text(encoding="utf-8"))
        assert list(fm["domains"]) == ["industrial", "robotics"], (sid, "domains")
        assert list(fm["axiom"]["standards"]) == expected, (sid, "frontmatter")
        manifest = yaml.safe_load(
            (ROOT / entry["path"] / "manifest.yaml").read_text(encoding="utf-8"))
        assert manifest["standards"] == expected, (sid, "manifest")
        assert manifest["facets"]["domains"] == ["industrial", "robotics"], (sid, "facets")
        standard_map = (ROOT / entry["path"] / "references" / "standard-map.md").read_text(
            encoding="utf-8")
        for std in expected:
            assert std.split(":")[0] in standard_map, (sid, std)
            family = _family_of(std)
            assert (ROOT / "standards" / "industrial" / f"{family}.yaml").exists(), (sid, std)


def test_assurance_dependent_links_symmetric():
    import yaml
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    idx = {e["id"]: e for e in cat["skills"]}
    for builder, existing in DEPENDENT_LINKS.items():
        assert existing in (idx[builder].get("related_skills") or []), (builder, existing)
        assert builder in (idx[existing].get("related_skills") or []), (existing, builder)
