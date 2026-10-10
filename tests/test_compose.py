# SPDX-License-Identifier: Apache-2.0
"""Prompt-driven composer: mind-map DAG, traceability chains, interface agreement."""

import json
import subprocess
import sys

from axiom_mcp.server import dispatch

from packages import axiom_sdk

PROMPT = ("AUTOSAR Classic ECU: analyse diagnostic requirements, develop UDS server code, "
          "generate positive and negative test cases, review code, "
          "map requirements to code and tests")


def test_diag_prompt_composes_full_chain():
    mind = axiom_sdk.compose_mindmap(PROMPT, domain="automotive",
                                     platform="autosar-classic",
                                     standards=["ISO 14229-1"])
    assert mind["axes"]["domain"] == "automotive"
    assert mind["stages"] == ["requirements", "implementation", "tests",
                              "review", "traceability"]
    impl = next(link for link in mind["chain"] if link["stage"] == "implementation")
    assert "automotive-diagnostics" in impl["skills"]
    assert "diag-uds-testgen" in mind["tools"]
    assert any(e["via"] == "REQ->CODE" for e in mind["edges"])
    assert any(e["via"] == "REQ->TEST" for e in mind["edges"])
    assert any(c["id"] == "REQ-TEST" for c in mind["trace_chains"])
    assert mind["orchestrator"] == "skill-orchestrator"
    assert "flowchart LR" in mind["mermaid"]


def test_narrow_prompt_selects_stages_only():
    mind = axiom_sdk.compose_mindmap("review the UDS server code",
                                     domain="automotive", platform="mcu")
    assert mind["stages"] == ["implementation", "review"]


def test_empty_prompt_gives_full_chain_over_all_axes():
    mind = axiom_sdk.compose_mindmap("", domain="automotive", platform="mcu",
                                     os="autosar-classic", language="c",
                                     hardware="arm-cortex-m", technology="mcu")
    assert mind["stages"] == ["requirements", "architecture", "implementation",
                              "tests", "review", "traceability", "evidence"]
    assert mind["axes"]["hardware"] == "arm-cortex-m"


def test_cli_mcp_agree_with_sdk():
    expected = axiom_sdk.compose_mindmap(PROMPT, domain="automotive",
                                         platform="autosar-classic")
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "compose", PROMPT,
         "--domain", "automotive", "--platform", "autosar-classic"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout) == expected
    resp = dispatch("tools/call", {"name": "compose", "arguments": {
        "prompt": PROMPT, "domain": "automotive", "platform": "autosar-classic"}})
    assert resp == expected
