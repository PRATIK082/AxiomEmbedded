"""Skill framework tests: catalog, loader, validator, runner, SDK/MCP wiring."""
from __future__ import annotations
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXEMPLARS = ["axiom-autosar-classic-bsw-integration", "axiom-diagnostics-uds"]


def test_catalog_lists_every_skill():
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    ids = [e["id"] for e in cat["skills"]]
    assert len(ids) == len(set(ids))
    axiom_ids = [i for i in ids if i.startswith("axiom-")]
    assert len(axiom_ids) == 35
    on_disk = {p.name for p in (ROOT / "skills").iterdir()
               if p.is_dir() and (p / "SKILL.md").exists()
               and not p.name.startswith(("_", "."))}
    assert set(ids) == on_disk
    mats = {e["maturity"] for e in cat["skills"]}
    assert mats <= {"experimental", "beta", "production"}


def test_registry_yaml_consistent_with_catalog():
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    reg = yaml.safe_load((ROOT / "skills" / "registry.yaml").read_text(encoding="utf-8"))
    cat_ids = {e["id"] for e in cat["skills"]}
    reg_paths = {s["path"] for s in reg["skills"]}
    assert cat_ids == {p.split("/", 1)[1] for p in reg_paths}


def test_loader_validates_exemplars():
    from packages.skills.loader import validate_skill_doc
    for sid in EXEMPLARS:
        rep = validate_skill_doc(sid)
        assert rep["valid"], (sid, rep["errors"])


def test_loader_rejects_unknown_skill():
    from packages.skills.loader import validate_skill_doc
    rep = validate_skill_doc("axiom-does-not-exist")
    assert not rep["valid"]


def test_runner_dry_run_writes_nothing(tmp_path):
    from packages.skills.runner import run_skill
    before = list(tmp_path.rglob("*"))
    out = run_skill(EXEMPLARS[0], repo_path=".", target_files=["a/b.c"],
                    objective="t", dry_run=True)
    assert out["status"] == "dry-run"
    assert list(tmp_path.rglob("*")) == before
    assert out["manifest"]["skill"] == EXEMPLARS[0]


def test_runner_apply_writes_manifest(tmp_path):
    from packages.skills.runner import run_skill
    out = run_skill(EXEMPLARS[1], repo_path=".", objective="t",
                    output_dir=str(tmp_path), dry_run=False)
    assert out["status"] == "ok"
    assert (pathlib.Path(out["run_dir"]) / "run-manifest.json").exists()


def test_runner_rejects_path_traversal(tmp_path):
    import pytest
    from packages.skills.runner import run_skill
    with pytest.raises(ValueError):
        run_skill(EXEMPLARS[0], target_files=["../evil"], dry_run=True,
                  output_dir=str(tmp_path))


def test_exemplar_checker_scripts():
    import sys
    sys.path.insert(0, str(ROOT / "skills" / EXEMPLARS[0] / "scripts"))
    sys.path.insert(0, str(ROOT / "skills" / EXEMPLARS[1] / "scripts"))
    import check_bsw
    import check_uds_matrix
    assert check_bsw.check_config("RTE OS COM PduR CanIf CanTp Dcm Dem NvM EcuM ports runnables events signals")["verdict"] == "PASS"
    assert check_uds_matrix.check_matrix({"services": []}) != []


def test_sdk_search_and_mcp_tools_registered():
    from packages import axiom_sdk
    from axiom_mcp.server import TOOLS
    res = axiom_sdk.search_skills("bsw", domain="automotive")
    assert res["count"] >= 1
    for t in ("search_skills", "validate_skill", "run_skill", "create_skill",
              "skill_manifest", "list_skills", "read_skill"):
        assert t in TOOLS


def test_manifest_matches_frontmatter_all_skills():
    import yaml as _yaml
    from packages import axiom_sdk
    from packages.skills.loader import parse_skill_doc
    cat = _yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    for e in cat["skills"]:
        m = axiom_sdk.skill_manifest(e["id"])
        fm, _ = parse_skill_doc(
            (ROOT / e["path"] / "SKILL.md").read_text(encoding="utf-8"))
        assert m["id"] == fm["name"] == e["id"]
        assert m["version"] == str(fm["version"])
        assert m["applicable_domains"] == list(fm.get("domains", []))
        assert m["applicable_platforms"] == list(fm.get("platforms", []))
        assert m["category"].startswith("domains/")
        assert "SKILL.md" in m["derived_from"]


def test_links_resolve_and_extends_terminates():
    import yaml as _yaml
    from packages.skills.registry import index_catalog, resolve_extends
    cat = _yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    idx = index_catalog(cat)
    for e in cat["skills"]:
        for rel in (e.get("related_skills", []) or []) + (e.get("sub_skills", []) or []):
            assert rel in idx, (e["id"], rel)
        base = e.get("extends")
        if base:
            assert base in idx
        chain = resolve_extends(e["id"], idx)
        assert len(chain) <= len(idx)
    # spot checks: no duplicates created, links are bidirectional-safe
    assert idx["autosar"]["sub_skills"]
    assert "autosar" in idx["axiom-autosar-classic-bsw-integration"]["related_skills"]


CROSS_DOMAIN_NEW = [
    "axiom-interface-contract-design",
    "axiom-static-analysis-triage",
    "axiom-embedded-cicd",
    "axiom-architecture-decision-records",
    "axiom-technical-debt-assessment",
]


def test_catalog_facet_parity_with_frontmatter():
    import yaml as _yaml
    from packages.skills.loader import parse_skill_doc
    cat = _yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    for e in cat["skills"]:
        if not e["id"].startswith("axiom-"):
            continue
        fm, _ = parse_skill_doc(
            (ROOT / e["path"] / "SKILL.md").read_text(encoding="utf-8"))
        ax = fm.get("axiom", {}) or {}
        for facet in ("lifecycle", "standards", "artifact_types", "mcp_tools",
                      "risk_level", "review_required"):
            assert e.get(facet) == ax.get(facet), (e["id"], facet)


def test_cross_domain_skills_complete():
    from packages.skills.loader import validate_skill_doc
    for sid in CROSS_DOMAIN_NEW:
        d = ROOT / "skills" / sid
        assert (d / "SKILL.md").exists(), sid
        assert (d / "manifest.yaml").exists(), sid
        assert (d / "checklists" / "review.yaml").exists(), sid
        assert list((d / "templates").glob("*.template.*")), sid
        rep = validate_skill_doc(sid)
        assert rep["valid"], (sid, rep["errors"])


def test_triage_classifier_deterministic(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "skills" / "axiom-static-analysis-triage" / "scripts"))
    import classify_findings
    findings = tmp_path / "f.csv"
    findings.write_text(
        "finding_id,file,line,rule,severity,message\n"
        "F-0002,src/a.c,10,R1,warning,m1\n"
        "F-0001,src/b.c,20,R2,required,m2\n", encoding="utf-8")
    base = tmp_path / "b.csv"
    base.write_text("finding_id\nF-0002\n", encoding="utf-8")
    rows = classify_findings.classify(findings, base)
    assert [r["finding_id"] for r in rows] == ["F-0001", "F-0002"]
    assert rows[0]["bucket"] == "new" and rows[0]["gate_class"] == "blocker"
    assert rows[1]["bucket"] == "carried" and rows[1]["gate_class"] == "major"
    assert classify_findings.classify(findings, base) == rows
