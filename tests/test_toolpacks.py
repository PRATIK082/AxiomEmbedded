# SPDX-License-Identifier: Apache-2.0
"""Plug-and-play toolpacks: domain/platform/standard selection + interface agreement."""

import io
import json
import subprocess
import sys

from axiom_mcp.server import dispatch

from packages import axiom_sdk


def test_automotive_mcu_selects_diag_packs():
    sel = axiom_sdk.select_toolpacks("automotive", "mcu")
    assert "diag-uds-testgen" in sel["tools"]
    assert "diag-extract-bridge" in sel["tools"]
    assert "test-generator" in sel["tools"]  # generic tooling always applies
    assert "diag-auto-review" in sel["agents"]
    pip = [p for item in sel["install"] for p in item["pip"]]
    assert any("acme-diag-extract" in p for p in pip)


def test_standard_filter_drops_unrelated_packs():
    sel = axiom_sdk.select_toolpacks("automotive", "mcu", ["ISO 26262"])
    assert "diag-uds-testgen" not in sel["tools"]  # ISO 14229-1-only pack
    assert "test-generator" in sel["tools"]  # generic pack survives
    sel14229 = axiom_sdk.select_toolpacks("automotive", "mcu", ["ISO 14229-1"])
    assert "diag-uds-testgen" in sel14229["tools"]


def test_generic_selection_covers_all_tools():
    sel = axiom_sdk.select_toolpacks()
    assert sel["tool_count"] == len(sel["tools"]) >= 12
    assert "diag-auto-review" in sel["agents"]  # unfiltered: every skill-anchored agent


def test_cli_mcp_agree_with_sdk():
    expected = axiom_sdk.select_toolpacks("automotive", "mcu", ["ISO 14229-1"])
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "packs", "--domain", "automotive",
         "--platform", "mcu", "--standard", "ISO 14229-1"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout) == expected
    resp = dispatch("tools/call", {"name": "packs", "arguments": {
        "domain": "automotive", "platform": "mcu", "standards": ["ISO 14229-1"]}})
    assert resp == expected
