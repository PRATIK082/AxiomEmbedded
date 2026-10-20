# SPDX-License-Identifier: Apache-2.0
"""Tool-candidate registry: contract, licence policy and interface agreement.

The candidate registry (`registries/tool-candidates.yaml`) is the proposal
surface for the pluggable tool packs. It is separate from the adopted
tool index (`registries/tool-index.json`): a candidate is a surveyed option,
not yet a shipped bridge.
"""

import json
import subprocess
import sys

from axiom_mcp.server import dispatch

from packages import axiom_sdk
from packages.toolpacks.candidates import (
    ADOPTABLE,
    INFORMATIONAL,
    load_candidates,
    select_candidates,
)
from scripts.validate_tool_candidates import validate


def test_registry_validates():
    problems = validate()
    assert problems == [], "tool candidate registry problems:\n" + "\n".join(problems)


def test_candidate_ids_are_unique():
    ids = [c["id"] for c in load_candidates()]
    assert len(ids) == len(set(ids))


def test_every_candidate_declares_the_required_contract():
    for cand in load_candidates():
        for key in ("id", "name", "upstream", "license", "channel",
                    "plugin_point", "status", "milestone"):
            assert cand.get(key), f"{cand.get('id')}: missing {key}"
        assert cand["upstream"].startswith("https://")


def test_adoptable_candidates_state_a_benefit_and_plugin_point():
    for cand in load_candidates():
        if cand["status"] in ADOPTABLE:
            assert cand.get("benefit"), f"{cand['id']}: no benefit stated"
            assert cand.get("plugin_point"), f"{cand['id']}: no plugin point"


def test_rejected_candidates_state_why():
    for cand in load_candidates():
        if cand["status"] == "rejected":
            assert cand.get("rejected_reason"), f"{cand['id']}: no rejected_reason"


def test_copyleft_tools_are_never_imported():
    """GPL/AGPL tools may be invoked, never linked into Axiom code."""
    for cand in load_candidates():
        licence = str(cand.get("license", "")).lower()
        if "gpl" in licence:
            assert cand.get("linkage") != "import", (
                f"{cand['id']}: copyleft licence {licence} must use linkage: subprocess"
            )


def test_informational_statuses_are_not_proposed_by_default():
    sel = axiom_sdk.list_tool_candidates()
    proposed = set(sel["candidates"])
    for cand in load_candidates():
        if cand["status"] in INFORMATIONAL:
            assert cand["id"] not in proposed


def test_selection_filters_by_facets():
    sel = axiom_sdk.list_tool_candidates("automotive", "mcu", ["ISO 14229-1"])
    assert sel["candidate_count"] == len(sel["candidates"]) > 0
    assert "udsoncan" in sel["candidates"]
    # generic platform tooling always applies
    assert "clang-tidy" in sel["candidates"]


def test_selection_filters_by_category_and_status():
    sel = select_candidates(category="diagnostics")
    assert sel["candidates"]
    assert all("diagnostics" in _categories(c["id"]) for c in sel["detail"])
    rejected = select_candidates(status="rejected")
    assert rejected["candidate_count"] >= 1
    assert all(c["status"] == "rejected" for c in rejected["detail"])


def test_selection_reports_install_channels():
    sel = axiom_sdk.list_tool_candidates()
    assert "pip" in sel["by_channel"]
    assert sel["pip_install"], "expected at least one pip-installable candidate"
    assert set(sel["by_milestone"]) <= {"M0", "M1", "M2", "M3", "M4", "M5"}


def test_cli_mcp_agree_with_sdk():
    expected = axiom_sdk.list_tool_candidates("automotive", "mcu", ["ISO 14229-1"])
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "tools", "--domain", "automotive",
         "--platform", "mcu", "--standard", "ISO 14229-1"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout) == expected
    resp = dispatch("tools/call", {"name": "tool_candidates", "arguments": {
        "domain": "automotive", "platform": "mcu", "standards": ["ISO 14229-1"]}})
    assert resp == expected


def _categories(candidate_id: str) -> list[str]:
    for cand in load_candidates():
        if cand["id"] == candidate_id:
            return list(cand.get("categories") or [])
    return []
