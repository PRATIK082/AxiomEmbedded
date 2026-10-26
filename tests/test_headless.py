# SPDX-License-Identifier: Apache-2.0
"""Keyless headless integration: the real `opencode` binary validates config,
MCP handshake, and the dry-run contract. Skipped when opencode is absent."""

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
OPENCODE = shutil.which("opencode")

requires_opencode = pytest.mark.skipif(
    OPENCODE is None, reason="opencode binary not on PATH")


def _axiom(*argv: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "axiom_cli", *argv],
        capture_output=True, text=True, cwd=ROOT, check=True,
    )
    return json.loads(proc.stdout)


@requires_opencode
def test_oc_dry_run_contract_against_real_binary():
    out = _axiom("oc", "run", "ping", "--dry-run")
    assert out["status"] == "dry-run"
    assert out["argv"][:2] == ["opencode", "run"]
    assert out["opencode"]["state"] in ("ok", "warn")
    assert pathlib.Path(out["env"]["OPENCODE_CONFIG"]).exists()


@requires_opencode
def test_opencode_accepts_axiom_config_and_mcp_handshake():
    """`opencode mcp list` loads the isolated config and completes the
    stdio handshake with `axiom mcp` (initialize + tools/list). Needs no
    API key and makes no model calls."""
    out = _axiom("oc", "run", "ping", "--dry-run")
    env = dict(os.environ, OPENCODE_CONFIG=out["env"]["OPENCODE_CONFIG"])
    if "OPENCODE_CONFIG_DIR" in out["env"]:
        env["OPENCODE_CONFIG_DIR"] = out["env"]["OPENCODE_CONFIG_DIR"]

    # OpenCode v2 runs as a client/server process: a client command connects
    # to an already-running service, so its config env is not enough to prove
    # isolation.  Start a private service with the launcher environment and
    # ask it to report the resolved config (which must include "axiom").
    proc = subprocess.run(
        [OPENCODE, "api", "--standalone", "GET", "/api/config"],
        capture_output=True, cwd=ROOT, env=env, timeout=120,
        encoding="utf-8", errors="replace",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "axiom" in proc.stdout, proc.stdout
    assert "failed" not in proc.stdout.lower(), proc.stdout

    # Also exercise the stdio handshake directly, without an API key or model
    # call, so a broken MCP server is caught even when OpenCode is v2.
    init = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2024-11-05",
                                  "capabilities": {},
                                  "clientInfo": {"name": "test",
                                                 "version": "1"}}})
    listed = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                         "params": {}})
    mcp = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "mcp"],
        input=init + "\n" + listed + "\n",
        capture_output=True, cwd=ROOT, timeout=30,
        encoding="utf-8", errors="replace",
    )
    assert mcp.returncode == 0, mcp.stdout + mcp.stderr
    assert "axiom-mcp" in mcp.stdout, mcp.stdout
