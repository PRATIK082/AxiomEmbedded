"""Contract tests for the CodeQL bridge (stubbed CLI, no CodeQL install)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load_shim() -> object:
    name = "codeql_bridge_shim"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE.parent / "bridge.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


shim = _load_shim()

CANNED_SARIF = {
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "CodeQL"}},
        "results": [
            {"ruleId": "cpp/autosar/c-style-arrays-used", "level": "error",
             "message": {"text": "C-style array used."},
             "locations": [{"physicalLocation": {
                 "artifactLocation": {"uri": "src/diag.c"},
                 "region": {"startLine": 42}}}]},
            {"ruleId": "c/misra/rule-17-13", "level": "warning",
             "message": {"text": "Possible side effect."},
             "locations": [{"physicalLocation": {
                 "artifactLocation": {"uri": "src/mem.c"},
                 "region": {"startLine": 7}}}]},
        ],
    }],
}


class _Proc:
    def __init__(self, stdout=""):
        self.stdout = stdout
        self.returncode = 0


def _fake_run_factory(monkeypatch, out_sarif: Path):
    calls = []

    def fake(cmd, **kwargs):
        calls.append(cmd)
        if cmd[:2] == ["codeql", "--version"]:
            return _Proc("CodeQL command-line toolchain release 2.23.9.\n")
        if cmd[1:3] == ["database", "analyze"]:
            prefixed = [a for a in cmd if a.startswith("--output=")]
            target = Path(prefixed[0].split("=", 1)[1]) if prefixed else out_sarif
            target.write_text(json.dumps(CANNED_SARIF), encoding="utf-8")
        return _Proc()

    monkeypatch.setattr(shim, "_RUN", fake)
    monkeypatch.setattr(shim.shutil, "which", lambda _: "/usr/bin/codeql")
    return calls


def test_run_ingests_sarif_findings(tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    calls = _fake_run_factory(monkeypatch, out / "results.sarif")
    info = shim.run(tmp_path / "src", "make", tmp_path / "db", out,
                    "cpp", ["autosar-cpp"], "2.63.0", "default")
    assert info["findings"] == 2
    assert "codeql/autosar-cpp-coding-standards@2.63.0" in info["packs"]
    findings = json.loads((out / "findings.json").read_text(encoding="utf-8"))
    assert findings[0]["file"] == "src/diag.c" and findings[0]["line"] == 42
    assert findings[0]["rule_id"] == "cpp/autosar/c-style-arrays-used"
    assert any(c[1:3] == ["pack", "download"] for c in calls)
    assert any("--format=sarifv2.1.0" in c for c in calls)


def test_audit_suite_ref_shape(tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    calls = _fake_run_factory(monkeypatch, out / "results.sarif")
    shim.run(tmp_path / "src", "make", tmp_path / "db", out,
             "c", ["misra-c"], "2.63.0", "audit")
    assert any(":codeql-suites/misra-c-audit.qls" in a for c in calls for a in c)


def test_unknown_pack_rejected(tmp_path):
    with pytest.raises(SystemExit):
        shim.pack_refs(["nosuch"], "1.0", "default")


def test_fails_closed_without_cli(tmp_path, monkeypatch):
    monkeypatch.setattr(shim.shutil, "which", lambda _: None)
    with pytest.raises(SystemExit) as exc:
        shim.run(tmp_path / "src", "make", tmp_path / "db", tmp_path / "out",
                 "c", ["misra-c"], "", "default")
    assert "CodeQL CLI not found" in str(exc.value)
