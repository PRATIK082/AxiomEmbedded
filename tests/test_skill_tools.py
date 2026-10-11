# SPDX-License-Identifier: Apache-2.0
"""Tests for packages/skill_tools.py (P1 generator wrappers) + MCP wiring."""

import csv
import io
import json

import pytest

from axiom_mcp.server import TOOLS, dispatch
from packages import axiom_sdk

SKILL = "axiom-diagnostics-uds"
GATE_IDS = {"scope", "method", "validation", "traceability", "review"}


def _fixture_repo(tmp_path):
    (tmp_path / "ecu").mkdir()
    (tmp_path / "ecu" / "swc.arxml").write_text("<AUTOSAR/>", encoding="utf-8")
    (tmp_path / "ecu" / "bus.dbc").write_text("VERSION ()", encoding="utf-8")
    (tmp_path / "ecu" / "main.c").write_text("int main(void){return 0;}\n",
                                             encoding="utf-8")
    (tmp_path / "trace.csv").write_text(
        "time,event,ecu\n0.0,boot,ECU1\n1.5,dtc,ECU1\n3.0,dtc,ECU2\n",
        encoding="utf-8")
    (tmp_path / "run.log").write_text(
        "boot ok\nERROR timeout on CAN\nfail to start\nall good\n",
        encoding="utf-8")
    return tmp_path


# --- analyze_repository ----------------------------------------------------

def test_analyze_repository_counts(tmp_path):
    repo = _fixture_repo(tmp_path)
    res = axiom_sdk.analyze_repository(str(repo))
    assert res["status"] == "ok"
    kinds = {a["artifact"]: a["files"] for a in res["artifacts"]}
    assert kinds.get("ARXML") == 1
    assert kinds.get("DBC") == 1
    assert kinds.get("C") == 1
    assert kinds.get("trace-data") == 1
    assert kinds.get("trace-log") == 1


def test_analyze_repository_bad_path():
    assert axiom_sdk.analyze_repository(
        "no-such-dir-xyz")["status"] == "error"


# --- generate_checklist ----------------------------------------------------

def test_checklist_dry_run_content():
    res = axiom_sdk.generate_checklist(SKILL)
    assert res["status"] == "ok"
    assert res["written"] is False
    assert {g["id"] for g in res["gates"]} == GATE_IDS
    assert res["markdown"].count("- [ ]") == len(res["gates"]) == 5


def test_checklist_write_confined(tmp_path):
    repo = _fixture_repo(tmp_path)
    res = axiom_sdk.generate_checklist(SKILL, "out/check.md", str(repo))
    assert res["written"] is True
    assert (repo / "out" / "check.md").exists()


def test_checklist_escape_rejected(tmp_path):
    repo = _fixture_repo(tmp_path)
    assert axiom_sdk.generate_checklist(
        SKILL, "../evil.md", str(repo))["status"] == "error"


def test_bad_skill_id_everywhere(tmp_path):
    repo = _fixture_repo(tmp_path)
    for fn in (axiom_sdk.generate_checklist, axiom_sdk.generate_test_plan,
               axiom_sdk.generate_traceability_matrix,
               axiom_sdk.generate_report):
        assert fn("../evil", None, str(repo))["status"] == "error"
    assert axiom_sdk.generate_checklist("no-such-skill")["status"] == "error"


# --- generate_test_plan / traceability -------------------------------------

def test_test_plan_rows_match_workflow():
    res = axiom_sdk.generate_test_plan(SKILL)
    assert res["status"] == "ok"
    assert len(res["rows"]) >= 1
    assert all(r["status"] == "Planned" for r in res["rows"])
    assert res["markdown"].count("| VT-") == len(res["rows"])


def test_traceability_csv_shape():
    res = axiom_sdk.generate_traceability_matrix(SKILL)
    assert res["status"] == "ok"
    rows = list(csv.reader(io.StringIO(res["csv"])))
    assert rows[0] == ["Step", "Activity", "Inputs", "Outputs", "Evidence",
                       "Status"]
    assert len(rows) - 1 == res["rows"] >= 1


# --- generate_report --------------------------------------------------------

def test_report_skill_context(tmp_path):
    repo = _fixture_repo(tmp_path)
    res = axiom_sdk.generate_report(SKILL, None, None, str(repo))
    assert res["status"] == "ok"
    assert "Review gates" in res["markdown"]


def test_report_run_manifest(tmp_path):
    repo = _fixture_repo(tmp_path)
    rd = repo / "run1"
    rd.mkdir()
    (rd / "run-manifest.json").write_text(json.dumps({
        "timestamp": "2026-01-01T00:00:00Z", "inputs": {"objective": "x"},
        "generated_files": ["a.md"], "acceptance_checks": ["ok"],
        "warnings": []}), encoding="utf-8")
    res = axiom_sdk.generate_report(SKILL, "run1", None, str(repo))
    assert res["status"] == "ok"
    assert "Run summary" in res["markdown"]
    assert res["run_manifest"]["timestamp"] == "2026-01-01T00:00:00Z"


def test_report_missing_run(tmp_path):
    repo = _fixture_repo(tmp_path)
    assert axiom_sdk.generate_report(
        SKILL, "nope", None, str(repo))["status"] == "error"


# --- review_configuration ---------------------------------------------------

def test_review_valid_yaml(tmp_path):
    repo = _fixture_repo(tmp_path)
    (repo / "ecu.yml").write_text("a: 1\nb:\n  - x\n", encoding="utf-8")
    res = axiom_sdk.review_configuration(SKILL, "ecu.yml", str(repo))
    assert res["verdict"] == "pass"
    assert any(f["check"] == "yaml-parse" and f["severity"] == "pass"
               for f in res["findings"])
    assert res["applicable_gates"]


def test_review_secret_scan_redacts(tmp_path):
    repo = _fixture_repo(tmp_path)
    (repo / "bad.yml").write_text("user: a\npassword: s3cr3t-hunter2\n",
                                  encoding="utf-8")
    res = axiom_sdk.review_configuration(SKILL, "bad.yml", str(repo))
    assert res["verdict"] == "fail"
    sec = next(f for f in res["findings"] if f["check"] == "secrets")
    assert "s3cr3t" not in sec["detail"]  # line numbers only
    assert "2" in sec["detail"]


def test_review_invalid_json_and_missing(tmp_path):
    repo = _fixture_repo(tmp_path)
    (repo / "bad.json").write_text("{oops", encoding="utf-8")
    assert axiom_sdk.review_configuration(
        SKILL, "bad.json", str(repo))["verdict"] == "fail"
    assert axiom_sdk.review_configuration(
        SKILL, "missing.yml", str(repo))["status"] == "error"
    assert axiom_sdk.review_configuration(
        SKILL, "../../etc/passwd", str(repo))["status"] == "error"


# --- analyze_trace -----------------------------------------------------------

def test_trace_csv(tmp_path):
    repo = _fixture_repo(tmp_path)
    res = axiom_sdk.analyze_trace("trace.csv", str(repo))
    assert res["status"] == "ok"
    assert res["rows"] == 3
    assert res["time_column"] == "time"
    assert res["time_range"] == [0.0, 3.0]
    assert res["histograms"]["event"] == {"boot": 1, "dtc": 2}


def test_trace_log_counts_only(tmp_path):
    repo = _fixture_repo(tmp_path)
    res = axiom_sdk.analyze_trace("run.log", str(repo))
    assert res["status"] == "ok"
    assert res["lines"] == 4
    assert res["keyword_hits"]["error"] == 1
    assert res["keyword_hits"]["fail"] == 1
    assert axiom_sdk.analyze_trace("missing.csv",
                                   str(repo))["status"] == "error"
    assert axiom_sdk.analyze_trace("../x.csv",
                                   str(repo))["status"] == "error"


# --- MCP wiring ---------------------------------------------------------------

def test_mcp_tools_registered():
    for name in ("analyze_repository", "generate_checklist",
                 "generate_test_plan", "generate_traceability_matrix",
                 "generate_report", "review_configuration", "analyze_trace"):
        assert name in TOOLS, name
        assert TOOLS[name]["inputSchema"]["type"] == "object"
    assert len(TOOLS) == 33


def test_mcp_dispatch_checklist():
    res = dispatch("tools/call", {"name": "generate_checklist",
                                  "arguments": {"skill_id": SKILL}})
    assert res["status"] == "ok"
    assert res["markdown"].count("- [ ]") == 5


def test_mcp_unknown_tool():
    with pytest.raises(ValueError):
        dispatch("tools/call", {"name": "nope", "arguments": {}})
