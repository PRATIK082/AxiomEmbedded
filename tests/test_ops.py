"""Slice 1 of Simple-UI feature: status dashboard + fix/feature plan emitters."""

from packages import axiom_ops as ops
from packages import axiom_sdk as sdk


def test_status_reports_all_skills():
    st = ops.get_status()
    assert st["project"] == "AxiomEmbedded"
    assert st["skills"]["total"] == 58
    assert st["skills"]["latest"] == "1.3.0"
    assert st["recommended_next_action"]


def test_fix_plan_has_ten_steps():
    plan = ops.plan_fix("ISSUE-123", domain="automotive", platform="mcu")
    assert plan["kind"] == "fix"
    assert len(plan["steps"]) == 10
    assert plan["steps"][0] == "intent" and plan["steps"][-1] == "pr"
    assert plan["approval_required_for"]


def test_feature_plan_has_nine_steps():
    plan = ops.plan_feature("FEATURE-22", domain="automotive", platform="mcu")
    assert plan["kind"] == "feature"
    assert len(plan["steps"]) == 9
    assert plan["engagement"]["skill_count"] == 50


def test_sdk_reexports_ops():
    assert sdk.get_status()["skills"]["total"] == 58
    assert len(sdk.plan_fix("ISSUE-1")["steps"]) == 10
    assert len(sdk.plan_feature("FEATURE-1")["steps"]) == 9


def test_dashboard_html_renders():
    from packages.axiom_server.server import dashboard_html

    html = dashboard_html()
    assert "AxiomEmbedded" in html
    assert "Recommended next action" in html
