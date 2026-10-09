# SPDX-License-Identifier: Apache-2.0
"""Phase 2a: `axiom oc` launcher — version gate, isolated config, dry-run."""

import json
import pathlib
import subprocess
import sys

import pytest

from packages import launcher
from packages.launcher import (
    build_command,
    ensure_isolated_config,
    execute,
    parse_version,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("text,expected", [
    ("1.18.31", (1, 18, 31)),
    ("opencode 1.18.35", (1, 18, 35)),
    ("v2.0.6", (2, 0, 6)),
    ("version: 1.19.0\n", (1, 19, 0)),
    ("no version here", None),
    ("", None),
])
def test_parse_version(text, expected):
    assert parse_version(text) == expected


class _Proc:
    def __init__(self, out: str):
        self.stdout, self.stderr = out, ""


def _patch_binary(monkeypatch, version_out: str):
    monkeypatch.setattr(launcher.shutil, "which", lambda _name: "/usr/bin/opencode")
    monkeypatch.setattr(launcher.subprocess, "run",
                        lambda *a, **k: _Proc(version_out))


@pytest.mark.parametrize("version_out,state", [
    ("1.18.31", "ok"),
    ("1.18.35", "ok"),
    ("1.18.40", "warn"),   # newer v1 than surveyed: warn, keep going
    ("1.17.0", "warn"),    # older than the tested floor: warn
    ("2.0.6", "fail"),     # untested major: fail closed
])
def test_status_matrix(monkeypatch, version_out, state):
    _patch_binary(monkeypatch, version_out)
    monkeypatch.delenv(launcher.OVERRIDE_ENV, raising=False)
    status = launcher.opencode_status()
    assert status["state"] == state
    assert status["binary"] == "/usr/bin/opencode"


def test_status_v2_override(monkeypatch):
    _patch_binary(monkeypatch, "2.0.6")
    monkeypatch.setenv(launcher.OVERRIDE_ENV, "1")
    assert launcher.opencode_status()["state"] == "warn"


def test_status_missing(monkeypatch):
    monkeypatch.setattr(launcher.shutil, "which", lambda _name: None)
    status = launcher.opencode_status()
    assert status["state"] == "fail" and status["binary"] is None


def test_status_unparseable(monkeypatch):
    _patch_binary(monkeypatch, "hello world")
    assert launcher.opencode_status()["state"] == "fail"


def test_isolated_config_from_checkout(tmp_path):
    cfg = ensure_isolated_config(tmp_path, model="anthropic/claude-x")
    data = json.loads(pathlib.Path(cfg["config_file"]).read_text(encoding="utf-8"))
    assert data["model"] == "anthropic/claude-x"
    assert data["mcp"]["axiom"]["type"] == "local"
    assert isinstance(data["mcp"]["axiom"]["command"], list)
    assert cfg["config_dir"] == str(ROOT / ".opencode")
    # Idempotent: second call rewrites the same bytes.
    before = pathlib.Path(cfg["config_file"]).read_bytes()
    ensure_isolated_config(tmp_path, model="anthropic/claude-x")
    assert pathlib.Path(cfg["config_file"]).read_bytes() == before


def test_isolated_config_without_content_source(tmp_path):
    src = tmp_path / "bare"
    src.mkdir()
    (src / "skills").mkdir()
    (src / "agents").mkdir()
    cfg = ensure_isolated_config(tmp_path / "home", source=src)
    assert cfg["config_dir"] is None
    assert "config-file isolation only" in cfg["note"]


def test_build_command():
    assert build_command("run", ["hello"], model="m", agent="a",
                         directory="d", fmt="json") == [
        "opencode", "run", "hello", "--model", "m", "--agent", "a",
        "--dir", "d", "--format", "json"]
    assert build_command("tui", [], directory="proj") == ["opencode", "proj"]
    assert build_command("run", [], title="t")[-2:] == ["--title", "t"]
    # `research` is an Axiom-side verb: it executes as `opencode run`.
    assert build_command("research", ["q"], agent="explore") == [
        "opencode", "run", "q", "--agent", "explore"]


def test_execute_dry_run_never_spawns(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(launcher, "opencode_status",
                        lambda: {"state": "ok", "binary": "opencode",
                                 "version": "1.18.31", "detail": "test"})
    def _boom(*a, **k):
        raise AssertionError("dry-run must not spawn a process")
    monkeypatch.setattr(launcher.subprocess, "run", _boom)
    rc = execute("run", ["hello"], model="m", dry_run=True, home=tmp_path)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "dry-run"
    assert out["argv"][:3] == ["opencode", "run", "hello"]
    assert "OPENCODE_CONFIG" in out["env"]
    assert out["isolated"] is True


def test_execute_refuses_without_opencode(monkeypatch, capsys):
    monkeypatch.setattr(launcher, "opencode_status",
                        lambda: {"state": "fail", "binary": None,
                                 "version": None, "detail": "missing"})
    assert execute("run", ["hi"], dry_run=True) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def _cli(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "axiom_cli", *argv],
                          capture_output=True, text=True, cwd=ROOT)


def test_cli_oc_help_without_binary():
    assert _cli("oc", "--help").returncode == 0
    assert _cli("oc", "run", "--help").returncode == 0


def test_doctor_reports_opencode():
    proc = _cli("doctor", "--skip-tests")
    assert proc.returncode == 0
    assert "- opencode:" in proc.stdout
