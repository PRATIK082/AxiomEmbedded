# SPDX-License-Identifier: Apache-2.0
"""Tests for rule-based skill groups (views over the catalog, no dir moves)."""

import json
import pathlib

import pytest
import yaml

from packages import axiom_sdk
from packages.skills import groups as groups_mod
from packages.skills.engage import engage
from packages.skills.registry import load_catalog

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_groups_cover_every_skill():
    cat = load_catalog()
    assert groups_mod.validate_groups(cat) == []


def test_unknown_match_key_rejected():
    cat = load_catalog()
    bad = {"schema_version": 1,
           "groups": {"nope": {"title": "Nope", "match_any": [{"bogus_key": "x"}]}}}
    with pytest.raises(ValueError):
        groups_mod.validate_groups(cat, bad)


def test_by_group_index_matches_matcher():
    cat = load_catalog()
    idx = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    for gid, members in groups_mod.group_members(cat).items():
        assert idx["by_group"][gid] == sorted(members), gid
    assert set(idx["by_group"]) == set(groups_mod.load_groups()["groups"])


def test_engage_group_filter_and_limit():
    res = engage(group="diagnostics")
    assert res["status"] == "ok"
    assert res["group"] == "diagnostics"
    assert res["total"] == len(res["skills"]) and not res["truncated"]
    limited = engage(group="diagnostics", limit=2)
    assert limited["total"] > 2
    assert len(limited["skills"]) == 2 and limited["truncated"] is True
    assert limited["limit"] == 2


def test_engage_unknown_group_errors():
    res = engage(group="does-not-exist")
    assert res["status"] == "error"


def test_engage_group_and_domain_combine():
    res = engage(domain="automotive", group="diagnostics")
    assert res["status"] == "ok"
    assert res["total"] >= 1


def test_install_groups_end_to_end(tmp_path):
    from packages.installer import install_client
    dest = tmp_path / "proj"
    res = install_client("opencode", dest, tmp_path / "home", ROOT,
                         is_global=False, groups=["diagnostics"])
    assert res["groups"] == ["diagnostics"]
    copied = [w for w in res["written"] if "/skills/" in w]
    assert copied, res
    idx = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    diag = set(idx["by_group"]["diagnostics"])
    for w in copied:
        sid = w.split("/skills/")[1].split("/")[0]
        entry = idx["skills"].get(sid, {})
        assert sid in diag or "all" in entry.get("domains", []), sid


def test_mcp_engage_group_passthrough():
    from axiom_mcp.server import dispatch
    res = dispatch("tools/call", {"name": "engage",
                                  "arguments": {"group": "diagnostics", "limit": 1}})
    assert res["status"] == "ok", res
    assert res["group"] == "diagnostics" and len(res["skills"]) == 1


def test_cli_engage_group_limit():
    import subprocess, sys
    out = subprocess.run([sys.executable, "-m", "axiom_cli", "engage",
                          "--group", "diagnostics", "--limit", "2"],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout)
    assert payload["group"] == "diagnostics" and len(payload["skills"]) == 2
