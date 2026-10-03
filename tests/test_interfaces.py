"""Interface agreement: SDK, CLI, MCP, REST, A2A return the same engagement."""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import urllib.request

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from packages import axiom_sdk as sdk  # noqa: E402
from packages.axiom_server.server import create_server  # noqa: E402


def test_sdk_engage_selectivity():
    sel = sdk.engage(domain="automotive", platform="mcu")
    assert sel["skill_count"] == 50
    assert "mcu" in sel["skills"] and "autosar" in sel["skills"]
    assert "automotive-mcu" in sel["profiles"]


def test_sdk_run_plan_shape():
    plan = sdk.run_plan("Add watchdog supervision", domain="automotive", platform="mcu")
    assert plan["mode"] == "plan-then-execute"
    assert plan["phases"] == ["plan", "implement", "verify", "evidence"]
    assert "git push" in plan["approval_required_for"]
    assert plan["engagement"]["skill_count"] == 50


def test_sdk_read_skill_unknown():
    with pytest.raises(KeyError):
        sdk.read_skill("no-such-skill")
    assert "MPU" in sdk.read_skill("mcu") or "Mpu" in sdk.read_skill("mcu") or len(sdk.read_skill("mcu")) > 1000


def _mcp_call(proc, mid, method, params=None):
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def test_mcp_agrees_with_sdk():
    proc = subprocess.Popen(
        [sys.executable, "-m", "axiom_cli", "mcp"],
        cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True, bufsize=1,
    )
    try:
        init = _mcp_call(proc, 1, "initialize")
        assert init["result"]["serverInfo"]["name"] == "axiom-embedded"
        tools = _mcp_call(proc, 2, "tools/list")
        assert {t["name"] for t in tools["result"]["tools"]} == {"engage", "run_plan", "read_skill", "list_skills", "list_profiles", "get_status", "plan_fix", "plan_feature"}
        eng = _mcp_call(proc, 3, "tools/call", {"name": "engage", "arguments": {"domain": "automotive", "platform": "mcu"}})
        assert json.loads(eng["result"]["content"][0]["text"])["skill_count"] == 50
        err = _mcp_call(proc, 4, "tools/call", {"name": "read_skill", "arguments": {"skill_id": "no-such-skill"}})
        assert err["result"].get("isError") is True
    finally:
        proc.kill()


def test_rest_and_a2a_agree_with_sdk():
    server = create_server(0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{port}"
        card = json.load(urllib.request.urlopen(f"{base}/.well-known/agent.json"))
        assert card["name"] == "axiom-embedded" and "a2a-task" in card["interfaces"]
        req = urllib.request.Request(base + "/v1/engage", data=json.dumps({"domain": "automotive", "platform": "mcu"}).encode(), headers={"Content-Type": "application/json"})
        assert json.load(urllib.request.urlopen(req))["skill_count"] == 50
        req = urllib.request.Request(base + "/v1/a2a/tasks", data=json.dumps({"message": "Add watchdog", "domain": "automotive", "platform": "mcu"}).encode(), headers={"Content-Type": "application/json"})
        task = json.load(urllib.request.urlopen(req))
        assert task["status"] == "completed" and task["artifact"]["engagement"]["skill_count"] == 50
        try:
            urllib.request.urlopen(f"{base}/v1/skills/no-such-skill")
            raise AssertionError("expected 404")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
    finally:
        server.shutdown()
