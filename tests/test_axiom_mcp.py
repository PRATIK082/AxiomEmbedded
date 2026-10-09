# SPDX-License-Identifier: Apache-2.0
"""Phase 1b: axiom_mcp exposes every CLI command as a typed stdio tool."""

import io
import json
import pathlib
import subprocess
import sys

import pytest
import yaml

from axiom_mcp.server import TOOLS, dispatch, serve

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Every axiom_cli command except the transports themselves (mcp/serve are the
# servers; install lands in Phase 1d).
EXPECTED_TOOLS = {
    "version", "doctor", "analyze", "graph_build", "context_select", "impact",
    "profile_validate", "workflow_plan", "route", "engage", "run_plan",
    "read_skill", "list_skills", "list_profiles", "status", "fix", "feature",
    "research", "install",
}


def test_tool_registry_covers_every_cli_command():
    assert EXPECTED_TOOLS <= set(TOOLS)


def test_every_tool_has_description_and_json_schema():
    for name, spec in TOOLS.items():
        assert spec["description"], name
        schema = spec["inputSchema"]
        assert schema["type"] == "object", name
        assert isinstance(schema.get("properties", {}), dict), name
        for req in schema.get("required", []):
            assert req in schema["properties"], (name, req)


def _call(name: str, arguments: dict | None = None):
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": name, "arguments": arguments or {}}}
    stdin, stdout = io.StringIO(json.dumps(req) + "\n"), io.StringIO()
    assert serve(stdin, stdout) == 0
    return json.loads(stdout.getvalue())


def test_tools_list_hides_handlers():
    res = dispatch("tools/list", {})
    assert {t["name"] for t in res["tools"]} == set(TOOLS)
    assert all("handler" not in t for t in res["tools"])


def test_unknown_tool_is_an_error_response():
    resp = _call("nope", {})
    assert resp["error"]["code"] == -32603
    assert "unknown tool" in resp["error"]["message"]


def test_version_and_doctor_tools():
    from axiom_cli import __version__

    assert _call("version")["result"] == {"axiom": __version__}
    doctor = _call("doctor")["result"]
    assert doctor["axiom"] == __version__ and doctor["source_checkout"] is True


def test_engage_run_plan_agree_with_cli():
    args = {"request": "add watchdog supervision", "domain": "automotive", "platform": "mcu"}
    plan = _call("run_plan", args)["result"]
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "run", args["request"],
         "--domain", "automotive", "--platform", "mcu"],
        capture_output=True, text=True, check=True,
    )
    assert plan == json.loads(out.stdout)


def test_skill_and_profile_discovery(tmp_path):
    skills = _call("list_skills")["result"]["skills"]
    assert "embedded-c" in skills
    assert _call("read_skill", {"skill_id": "embedded-c"})["result"]["id"] == "embedded-c"
    profiles = _call("list_profiles")["result"]["profiles"]
    assert profiles, "expected at least one profile"


def test_profile_validate_and_workflow_plan(tmp_path):
    prof = tmp_path / "p.yaml"
    prof.write_text(yaml.safe_dump({"id": "t", "version": "1", "domains": ["automotive"],
                                    "capabilities": ["x"], "entry": "brownfield",
                                    "lifecycle": "v-model"}))
    assert _call("profile_validate", {"path": str(prof)})["result"]["valid"] is True
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"id": "t"}))
    res = _call("profile_validate", {"path": str(bad)})["result"]
    assert res["valid"] is False and "capabilities" in res["missing"]
    plan = _call("workflow_plan", {"profile": str(prof)})["result"]
    assert plan["start_phase"] == "discovery"


def test_analyze_graph_context_impact_on_temp_tree(tmp_path):
    src = tmp_path / "fw"
    src.mkdir()
    (src / "main.c").write_text('#include "hal.h"\nint main(void){return 0;}\n')
    analyzed = _call("analyze", {"path": str(src)})["result"]
    assert analyzed["files_indexed"] >= 1
    index = pathlib.Path(analyzed["index"])
    assert index.exists()
    out = tmp_path / "idx.json"
    built = _call("graph_build", {"path": str(src), "output": str(out)})["result"]
    assert out.exists() and built["files_indexed"] >= 1
    selected = _call("context_select", {"index": str(out), "roots": ["main.c"]})["result"]
    assert "main.c" in selected["selected"]
    proj = tmp_path / "project.yaml"
    proj.write_text(yaml.safe_dump({"id": "demo", "lifecycle": "v-model", "entry": "brownfield"}))
    impact = _call("impact", {"path": str(proj)})["result"]
    assert impact["next_phase"] == "discovery"


def test_route_status_fix_feature_research():
    assert _call("route", {"request": "fix hardfault in isr"})["result"]["intent"]
    assert "recommended_next_action" in _call("status")["result"]
    assert _call("fix", {"issue_id": "ISS-1"})["result"]["steps"]
    assert _call("feature", {"feature_id": "F-1"})["result"]["steps"]
    research = _call("research", {"question": "ISO 26262 automotive safety",
                                  "backend": "local"})["result"]
    assert research["status"] == "ok"
    assert research["findings"]


def test_research_cli_matches_mcp_tool():
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "research", "ISO 26262 automotive safety",
         "--backend", "local"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout)["status"] == "ok"


def test_mcp_entry_point_module():
    out = subprocess.run(
        [sys.executable, "-m", "axiom_mcp"],
        input=json.dumps({"jsonrpc": "2.0", "id": 7, "method": "initialize", "params": {}}),
        capture_output=True, text=True, check=True,
    )
    result = json.loads(out.stdout)["result"]
    # MCP handshake shape (strict clients validate these three keys).
    assert result["serverInfo"]["name"] == "axiom-mcp"
    assert isinstance(result["protocolVersion"], str)
    assert isinstance(result["capabilities"], dict)


def test_install_tool_matches_cli(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    res = _call("install", {"client": "codex", "path": str(target)})["result"]
    assert res["client"] == "codex" and res["scope"] == "project"
    assert "[mcp_servers.axiom-embedded]" in (target / ".codex" / "config.toml").read_text(encoding="utf-8")
