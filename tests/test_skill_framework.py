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
    assert len(axiom_ids) == 30
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
              "list_skills", "read_skill"):
        assert t in TOOLS
