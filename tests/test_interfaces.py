"""Interface agreement: SDK/CLI/MCP/REST/A2A return the same slice."""

import io
import json
import subprocess
import sys
import threading
import urllib.request

import pytest

from packages import axiom_sdk
from packages.axiom_mcp.server import serve as mcp_serve
from packages.axiom_server.server import Handler
from http.server import ThreadingHTTPServer

DOMAIN, PLATFORM = "automotive", "mcu"


def _post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())


def test_sdk_slice_is_42():
    sel = axiom_sdk.engage_skills(DOMAIN, PLATFORM)
    assert sel["skill_count"] == 42
    assert "autosar" in sel["skills"] and "mcu" in sel["skills"]


def test_sdk_run_plan_shape():
    plan = axiom_sdk.run_plan("add watchdog supervision", DOMAIN, PLATFORM)
    assert plan["mode"] == "plan-then-execute"
    assert plan["engagement"]["skill_count"] == 42
    assert "git push" in plan["approval_required_for"]


def test_cli_engage_agrees_with_sdk():
    out = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "engage", "--domain", DOMAIN, "--platform", PLATFORM],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout)["skills"] == axiom_sdk.engage_skills(DOMAIN, PLATFORM)["skills"]


def test_mcp_engage_agrees_with_sdk():
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": "engage", "arguments": {"domain": DOMAIN, "platform": PLATFORM}}}
    stdin, stdout = io.StringIO(json.dumps(req) + "\n"), io.StringIO()
    mcp_serve(stdin, stdout)
    resp = json.loads(stdout.getvalue())
    assert resp["result"]["skills"] == axiom_sdk.engage_skills(DOMAIN, PLATFORM)["skills"]


def test_rest_and_a2a_agree_with_sdk():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{port}"
        _, eng = _post(base + "/v1/engage", {"domain": DOMAIN, "platform": PLATFORM})
        assert eng["skills"] == axiom_sdk.engage_skills(DOMAIN, PLATFORM)["skills"]
        _, run = _post(base + "/v1/run", {"request": "x", "domain": DOMAIN, "platform": PLATFORM})
        assert run["engagement"]["skill_count"] == 42
        _, task = _post(base + "/v1/a2a/tasks", {"id": "t1", "intent": {"request": "x", "domain": DOMAIN, "platform": PLATFORM}})
        assert task["status"] == "planned" and task["plan"]["engagement"]["skill_count"] == 42
        with urllib.request.urlopen(base + "/.well-known/agent.json") as resp:
            assert json.loads(resp.read().decode())["name"] == "axiom-embedded"
    finally:
        httpd.shutdown()
