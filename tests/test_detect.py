"""Prompt->domain auto-detection + evidence-based stage detection."""

import json

from packages.agents.router import detect_domain, route
from packages.workflow.stage import detect_stage, reconcile_stage, V_MODEL_ORDER


def test_detect_domain_automotive_keywords():
    assert detect_domain("Write UDS diagnostic server for this ECU") == "automotive"
    assert detect_domain("ASIL-D brake controller needs MISRA C") == "automotive"
    assert detect_domain("AUTOSAR adaptive ara::com service") == "automotive"
    assert detect_domain("HARA and SOTIF for ADAS") == "automotive"
    assert detect_domain("TARA per ISO 21434, R155 evidence") == "automotive"


def test_detect_domain_no_false_positives():
    # Generic English must not trigger: "can", "code", "body", "cal" excluded.
    assert detect_domain("can you fix the login bug") is None
    assert detect_domain("add a feature to the dashboard") is None
    assert detect_domain("review this code for checksums") is None
    assert detect_domain("the body of the email") is None


def test_route_still_works_alongside_detect():
    assert route("fix UDS bug on CAN-FD") == "debugging"
    assert detect_domain("fix UDS bug on CAN-FD") == "automotive"


def test_run_cmd_auto_detects_domain(capsys):
    from axiom_cli.main import run_cmd

    assert run_cmd("Write UDS diagnostics for the ECU", None, None) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["domain_source"] == "detected"
    assert plan["engagement"]["domain"] == "automotive"
    assert plan["engagement"]["skill_count"] > 0


def test_run_cmd_explicit_domain_wins(capsys):
    from axiom_cli.main import run_cmd

    assert run_cmd("Write UDS diagnostics", "automotive", "mcu") == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["domain_source"] == "explicit"
    assert plan["engagement"]["skill_count"] == 50


def test_detect_stage_empty(tmp_path):
    assert detect_stage(tmp_path)["stage"] is None


def test_detect_stage_progressive(tmp_path):
    (tmp_path / "requirements").mkdir()
    assert detect_stage(tmp_path)["stage"] == "concept"
    (tmp_path / "architecture").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    got = detect_stage(tmp_path)
    assert got["stage"] == "unit-verification"
    assert set(got["evidence"]) == {"concept", "system-architecture", "detailed-design", "unit-verification"}


def test_reconcile_declared_wins_on_conflict():
    rec = reconcile_stage("verification", "unit-verification")
    assert rec["conflict"] is True
    assert rec["recommended_stage"] == "unit-verification"
    assert rec["next_phase"] == "verification"


def test_reconcile_detection_used_when_no_declaration():
    rec = reconcile_stage("concept", None)
    assert rec["recommended_stage"] == "concept"
    assert rec["next_phase"] == "system-architecture"
    assert V_MODEL_ORDER.index("concept") == 0


def test_stage_cmd_json(tmp_path, capsys):
    from axiom_cli.main import stage_cmd

    (tmp_path / "requirements").mkdir()
    (tmp_path / "src").mkdir()
    assert stage_cmd(str(tmp_path), "profiles/automotive-mcu.yaml") == 0
    out = json.loads(capsys.readouterr().out)
    assert out["detected_stage"] == "detailed-design"
    assert out["declared_stage"] == "unit-verification"
    assert out["recommended_stage"] == "unit-verification"
