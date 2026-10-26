"""Eval task registry: Terminal-Bench-style seed set for agent/eval regressions.

Tasks are plain YAML under evaluation/tasks/ (stub agent dirs under
evaluation/agents/ stay as owner placeholders). The runner only *lists* and
*grades static expectations* today (skills slices, clarification flags,
token caps, mcp --check); live model grading is P3-follow-up work.
"""

from __future__ import annotations

import pathlib

import yaml

from packages.paths import ROOT
TASKS_DIR = ROOT / "evaluation" / "tasks"


def list_tasks() -> list[dict]:
    """Load every evaluation/tasks/EV-*.yaml sorted by id."""
    tasks = []
    if not TASKS_DIR.exists():
        return tasks
    for path in sorted(TASKS_DIR.glob("EV-*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            data["_file"] = path.name
            tasks.append(data)
        except Exception:
            continue
    return tasks


def grade(task_id: str, repo_root: str = ".") -> dict:
    """Grade one task's static expectations. No model calls."""
    from packages.agents.project_context import resolve_project_context
    from packages.skills.engage import engage

    task = next((t for t in list_tasks() if t.get("id") == task_id), None)
    if task is None:
        return {"status": "error", "task": task_id, "failures": ["unknown task id"]}
    failures: list[str] = []
    expect = task.get("expect", {}) or {}
    ctx = resolve_project_context(repo_root, task.get("prompt", ""))
    domain = task.get("domain") or ctx.get("domain")
    engagement = engage(domain, task.get("platform"))
    skills = engagement.get("skills", [])
    for wanted in expect.get("skills_contain", []):
        if wanted not in skills:
            failures.append(f"skill missing from slice: {wanted}")
    for wanted in expect.get("standards_contain", []):
        if wanted not in (ctx.get("standards") or []):
            failures.append(f"standard missing from context: {wanted}")
    if expect.get("clarifies") and not ctx.get("needs_clarification"):
        failures.append("expected a clarification question, got none")
    cap = expect.get("primary_skill_cap")
    if cap and len(ctx.get("load_plan", {}).get("primary", [])) > cap:
        failures.append("primary skill slice exceeds cap")
    if "min_tool_count" in expect:
        from axiom_mcp.server import check as mcp_check

        report = mcp_check()
        if report.get("status") != expect.get("mcp_status", "ok"):
            failures.append(f"mcp --check status: {report.get('status')}")
        if report.get("tool_count", 0) < expect["min_tool_count"]:
            failures.append(f"mcp tool_count below {expect['min_tool_count']}")
    return {"status": "ok" if not failures else "fail",
            "task": task_id, "failures": failures,
            "domain": domain, "skill_count": len(skills)}
