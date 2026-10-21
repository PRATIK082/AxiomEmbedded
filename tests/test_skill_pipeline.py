# SPDX-License-Identifier: Apache-2.0
"""Tests for the one-command skill pipeline + domain-filtered install."""

import json
import pathlib

import pytest

from packages import axiom_sdk
from packages.installer import _filter_skill_relpaths, install_client

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_pipeline_check_clean_tree():
    rep = axiom_sdk.skill_pipeline(check=True)
    assert rep["status"] == "ok", rep
    assert rep["mode"] == "check"
    assert any(s["step"] == "validate" and s["status"] == "OK" for s in rep["steps"])


def test_pipeline_apply_idempotent():
    before = axiom_sdk.skill_pipeline(check=True)
    assert before["status"] == "ok"
    applied = axiom_sdk.skill_pipeline(check=False)
    assert applied["status"] == "ok", applied
    assert [s["step"] for s in applied["steps"]] == [
        "enrich", "sync-index", "sync-clients", "validate"]
    after = axiom_sdk.skill_pipeline(check=True)
    assert after["status"] == "ok"


def test_pipeline_mcp_check_only_by_default():
    from axiom_mcp.server import dispatch
    res = dispatch("tools/call", {"name": "skill_pipeline", "arguments": {}})
    assert res["status"] == "ok", res
    assert res["mode"] == "check"


def test_pipeline_check_ignores_client_mirrors_created_by_the_writers(monkeypatch):
    """Regression: --check must not report the writers' own output as drift.

    Client mirrors (.claude/, .opencode/) are gitignored build outputs. A
    clean checkout has none, so the writers create them. Comparing a
    before/after file *set* therefore reported STALE on every clean checkout
    of main. The check must hash the same path set on both sides.
    """
    import scripts.skill_pipeline as sp

    real = sp._generated_files
    calls = {"n": 0}

    def fake_generated_files():
        calls["n"] += 1
        if calls["n"] == 1:
            # A clean checkout: only the tracked generated files exist.
            return [p for p in real()
                    if ".claude" not in p.parts and ".opencode" not in p.parts]
        # The writers have just created the client mirrors.
        return real()

    monkeypatch.setattr(sp, "_generated_files", fake_generated_files)
    rep = sp.run_pipeline(check=True)
    assert rep["status"] == "ok", rep
    step = next(s for s in rep["steps"] if s["step"] == "writers-idempotent")
    assert step["status"] == "OK", step


def test_domain_filter_keeps_all_and_matching(tmp_path):
    idx = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    any_domain = next(d for s in idx["skills"].values() for d in s.get("domains", []) if d != "all")
    rels = [".opencode/skills/axiom-architecture-decision-records/SKILL.md",  # domains=[all]
            ".opencode/agents/planner.md"]
    for sid, entry in idx["skills"].items():
        if entry.get("domains") and "all" not in entry["domains"] and any_domain not in entry.get("domains", []):
            rels.append(f".opencode/skills/{sid}/SKILL.md")
            break
    keep, note = _filter_skill_relpaths(ROOT, rels, [any_domain])
    assert ".opencode/skills/axiom-architecture-decision-records/SKILL.md" in keep
    assert ".opencode/agents/planner.md" in keep  # non-skills untouched
    assert len(keep) == 2, note
    keep_all, _ = _filter_skill_relpaths(ROOT, rels, None)
    assert keep_all == rels


def test_install_domains_end_to_end(tmp_path):
    dest = tmp_path / "proj"
    res = install_client("opencode", dest, tmp_path / "home", ROOT, is_global=False,
                         domains=["robotics"])
    assert res["domains"] == ["robotics"]
    assert any("domains=[" in n for n in res["notes"])
    copied_skills = [w for w in res["written"] if "/skills/" in w]
    assert copied_skills, res
    idx = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    for w in copied_skills:
        sid = w.split("/skills/")[1].split("/")[0]
        doms = set(idx.get("skills", {}).get(sid, {}).get("domains", []))
        assert "all" in doms or "robotics" in doms, (sid, doms)
