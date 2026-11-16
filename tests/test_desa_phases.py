"""DESA Phase 2/5/6 tests: facets, activity routing, standards lifecycle, separation."""
from __future__ import annotations

import yaml

from packages.paths import ROOT
from packages.skills.groups import _clause_matches, group_members, load_groups
from packages.skills.registry import load_catalog
from packages.skills.validator import desa_checks


def _catalog():
    return load_catalog(ROOT / "skills" / "catalog.yaml")


def test_desa_facets_present():
    cat = _catalog()
    axiom_entries = [e for e in cat["skills"] if e["id"].startswith("axiom-")]
    assert axiom_entries
    for e in axiom_entries:
        for facet in ("activity", "capability_kind", "primary_domain",
                      "risk_class", "lifecycle_phases", "standard_ids"):
            assert facet in e, f"{e['id']} missing {facet}"


def test_group_matcher_supports_activity():
    assert _clause_matches({"id": "x", "activity": "code-review"}, {"activity": ["code-review"]})
    assert not _clause_matches({"id": "x", "activity": "code-review"}, {"activity": ["testing"]})


def test_groups_cover_all_enabled():
    from packages.skills.groups import validate_groups
    assert validate_groups(_catalog()) == []


def test_desa_unknown_activity_warns():
    _, warns = desa_checks("s", {"activity": "no-such-activity-xyz"})
    assert any("unknown activity" in w for w in warns)


def test_desa_unknown_standard_warns():
    _, warns = desa_checks("s", {"standard_ids": ["no-such-standard-xyz"]})
    assert any("not in standards/registry" in w for w in warns)


def test_standards_lifecycle_no_silent_replace():
    regs = yaml.safe_load((ROOT / "standards" / "registry.yaml").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in regs["standards"]}
    # Published editions that have proposed successors must keep published status.
    assert by_id["iso-sae-21434"]["status"] == "published"
    assert by_id["misra-c"]["status"] == "published"
    # Draft/pre-release entries, if any, must be explicitly marked.
    for sid, s in by_id.items():
        assert s["status"] in ("published", "draft", "pre-release",
                               "proposed", "withdrawn", "superseded"), sid


def test_domain_separation_aerospace_vs_autosar():
    members = group_members(_catalog(), load_groups())
    aero = set(members.get("aerospace-defense", []))
    autosar = set(members.get("autosar-classic", []))
    # Shared safety/review skills may overlap by design (safety-security group),
    # but platform-specific groups must not be identical.
    assert aero and autosar
    assert aero != autosar


def test_engage_activity_filter_returns_subset():
    from packages.skills.engage import engage
    full = engage()
    assert full["total"] == 261
    sub = engage(activity="functional-safety")
    assert sub["status"] == "ok"
    assert 0 < sub["skill_count"] < full["total"]
    assert "activity" in sub and sub["activity"] == "functional-safety"
    assert "axiom-functional-safety" in sub["skills"]


def test_engage_unknown_activity_warns_missing_context():
    # Phase 6 missing-context probe: unindexed activity must not silently
    # return an empty set; it carries an explicit warning.
    from packages.skills.engage import engage
    res = engage(activity="no-such-activity-xyz")
    assert res["status"] == "ok"
    assert res["skill_count"] == 0
    assert "warning" in res and "no-such-activity-xyz" in res["warning"]


def test_all_catalog_entries_have_valid_activity():
    import yaml as _yaml
    acts = (_yaml.safe_load((ROOT / "taxonomies" / "activities.yaml").read_text(encoding="utf-8")))
    valid = set(acts.get("activities", acts))
    cat = _catalog()
    for e in cat["skills"]:
        assert e.get("activity", "") in valid, f"{e['id']} bad activity {e.get('activity')!r}"
