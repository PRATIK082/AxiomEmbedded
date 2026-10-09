# SPDX-License-Identifier: Apache-2.0
"""Phase 1d: axiom install --client works per client in a temp project."""

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLIENTS = ["opencode", "claude", "codex", "gemini", "copilot"]


def run_install(*argv: str, cwd: pathlib.Path) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "axiom_cli", "install", *argv],
        capture_output=True, text=True, check=True, cwd=cwd,
    )
    return json.loads(proc.stdout)


@pytest.mark.parametrize("client", CLIENTS)
def test_install_project_scope(tmp_path, client):
    proj = tmp_path / "demo"
    proj.mkdir()
    first = run_install("--client", client, "--path", str(proj), cwd=ROOT)
    assert first["status"] == "ok" and first["client"] == client
    assert first["scope"] == "project"
    second = run_install("--client", client, "--path", str(proj), cwd=ROOT)
    assert second["written"] == [], f"second install must be a no-op: {second}"
    assert all(m.endswith("#present") for m in second["merged"]), second


def test_opencode_project_files(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    res = run_install("--client", "opencode", "--path", str(proj), cwd=ROOT)
    assert (proj / "opencode.json").exists()
    data = json.loads((proj / "opencode.json").read_text(encoding="utf-8"))
    entry = data["mcp"]["axiom-embedded"]
    assert entry["type"] == "local" and isinstance(entry["command"], list)
    assert (proj / ".opencode" / "agents" / "implementation.md").exists()
    assert (proj / ".opencode" / "skills" / "embedded-c" / "SKILL.md").exists()
    assert any("implementation.md" in w for w in res["written"])
    # Phase 2b: installer also ships /axiom-* commands and the policy plugin.
    assert (proj / ".opencode" / "commands" / "axiom-research.md").exists()
    assert (proj / ".opencode" / "commands" / "axiom-status.md").exists()
    assert (proj / ".opencode" / "plugins" / "axiom-policy.ts").exists()
    second = run_install("--client", "opencode", "--path", str(proj), cwd=ROOT)
    assert second["written"] == [], f"second install must be a no-op: {second}"


def test_claude_codex_gemini_copilot_project_files(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    run_install("--client", "claude", "--path", str(proj), cwd=ROOT)
    assert "axiom-embedded" in json.loads((proj / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    assert (proj / ".claude" / "skills" / "embedded-c" / "SKILL.md").exists()
    run_install("--client", "codex", "--path", str(proj), cwd=ROOT)
    assert "[mcp_servers.axiom-embedded]" in (proj / ".codex" / "config.toml").read_text(encoding="utf-8")
    run_install("--client", "gemini", "--path", str(proj), cwd=ROOT)
    assert "axiom-embedded" in json.loads((proj / ".gemini" / "settings.json").read_text(encoding="utf-8"))["mcpServers"]
    assert (proj / "GEMINI.md").exists()
    run_install("--client", "copilot", "--path", str(proj), cwd=ROOT)
    assert "AGENTS.md" in (proj / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")


def test_install_never_clobbers_user_content(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".github").mkdir(parents=True)
    mine = proj / ".github" / "copilot-instructions.md"
    mine.write_text("mine", encoding="utf-8")
    res = run_install("--client", "copilot", "--path", str(proj), cwd=ROOT)
    assert mine.read_text(encoding="utf-8") == "mine"
    assert ".github/copilot-instructions.md" in res["skipped"]


def test_install_merges_existing_opencode_json(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    cfg = proj / "opencode.json"
    cfg.write_text(json.dumps({"permission": {"edit": "ask"}}), encoding="utf-8")
    run_install("--client", "opencode", "--path", str(proj), cwd=ROOT)
    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert data["permission"] == {"edit": "ask"}
    assert data["mcp"]["axiom-embedded"]["type"] == "local"


@pytest.mark.parametrize("client", CLIENTS)
def test_install_global_scope_uses_home(tmp_path, client):
    home, proj = tmp_path / "home", tmp_path / "proj"
    home.mkdir()
    proj.mkdir()
    res = run_install("--client", client, "--global", "--home", str(home), "--path", str(proj), cwd=ROOT)
    assert res["scope"] == "global"
    assert not list(proj.rglob("*")), f"project dir must stay untouched: {res}"
