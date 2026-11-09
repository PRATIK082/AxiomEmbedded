"""Skill runner: structured dry-run + manifest-producing execution (no shell, no net)."""
from __future__ import annotations
import datetime
import json
import pathlib
import re
import sys

from packages.skills.loader import load_skill

from packages.paths import ROOT
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _safe_rel(p: str) -> pathlib.Path:
    pp = pathlib.Path(p)
    if pp.is_absolute() or ".." in pp.parts:
        raise ValueError(f"unsafe path: {p!r}")
    return pp


def run_skill(skill_id: str, repo_path: str = ".", target_files: list[str] | None = None,
              objective: str = "", constraints: str = "",
              output_dir: str | None = None, dry_run: bool = True,
              mode: str = "run", approval_token: str | None = None) -> dict:
    if not ID_RE.match(skill_id):
        raise ValueError(f"invalid skill id: {skill_id!r}")
    s = load_skill(skill_id)
    fm = s["frontmatter"]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    targets = [str(_safe_rel(t)) for t in (target_files or [])]
    # tool selection: required + optional from axiom block
    ax = fm.get("axiom", {}) or {}
    tools = list(ax.get("required_tools", []) or []) + [
        t for t in (ax.get("optional_tools", []) or [])]
    # catalog links (extends/related/sub-skills/overlays); tolerant if absent
    links: dict = {}
    try:
        from packages.skills.registry import load_catalog, resolve_extends
        _cat = load_catalog()
        _idx = {e["id"]: e for e in _cat.get("skills", [])}
        _entry = _idx.get(skill_id, {})
        links = {
            "extends": _entry.get("extends"),
            "extends_chain": resolve_extends(skill_id, _idx),
            "related_skills": _entry.get("related_skills", []),
            "sub_skills": _entry.get("sub_skills", []),
            "domain_overlays": _entry.get("domain_overlays", []),
            "platform_overlays": _entry.get("platform_overlays", []),
        }
        if _entry.get("extends"):
            base = _entry["extends"]
    except Exception:
        links = {"extends": None, "extends_chain": [], "related_skills": [],
                 "sub_skills": [], "domain_overlays": [], "platform_overlays": []}
    manifest = {
        "skill": skill_id,
        "version": str(fm.get("version")),
        "timestamp": ts,
        "links": links,
        "inputs": {"repo_path": repo_path, "target_files": targets,
                   "objective": objective, "constraints": constraints},
        "selected_tools": tools,
        "decisions": [f"loaded skill {skill_id} v{fm.get('version')}",
                      f"dry_run={dry_run}"] +
        ([f"base context: {links['extends']}"] if links.get("extends") else []),
        "generated_files": [],
        "warnings": [],
        "acceptance_checks": ["SKILL.md sections present",
                              f"dry-run={dry_run} => no writes" if dry_run
                              else "artifacts written under output dir"],
    }
    # Discover checker scripts shipped with the skill.
    skill_dir = ROOT / "skills" / skill_id
    checkers = sorted((skill_dir / "scripts").glob("check_*.py")) if (skill_dir / "scripts").is_dir() else []
    ax = fm.get("axiom", {}) or {}
    safety_critical = ax.get("safety_critical") is True
    # Plan mode: emit + validate a structured plan, no execution.
    if mode == "plan":
        plan_errors = []
        if not objective:
            plan_errors.append("objective is required for plan mode")
        if not targets:
            plan_errors.append("target_files is required for plan mode")
        plan = dict(manifest)
        plan["mode"] = "plan"
        plan["safety_critical"] = safety_critical
        plan["approval_required"] = safety_critical
        plandir = (pathlib.Path(output_dir) if output_dir else pathlib.Path(repo_path)) / ".axiom" / "plans" / ts / skill_id
        plandir.mkdir(parents=True, exist_ok=True)
        (plandir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        return {"status": "plan", "valid": not plan_errors, "errors": plan_errors,
                "plan_path": str(plandir / "plan.json"), "manifest": plan,
                "summary": f"{skill_id}: plan {'valid' if not plan_errors else 'INVALID'}"}
    # Safety gate: safety-critical skills require approval_token to apply.
    if safety_critical and not dry_run and not approval_token:
        return {"status": "approval-required", "manifest": manifest,
                "summary": f"{skill_id}: safety_critical requires approval_token"}
    if dry_run:
        for c in checkers:
            manifest["decisions"].append(f"would run checker: {c.relative_to(ROOT)}")
        manifest["decisions"].append(
            f"would write run manifest to .axiom/runs/{ts}/{skill_id}/run-manifest.json")
        return {"status": "dry-run", "manifest": manifest,
                "summary": f"{skill_id}: dry-run OK, {len(targets)} target(s), "
                           f"{len(tools)} tool(s) selected, {len(checkers)} checker(s)"}
    out = pathlib.Path(output_dir) if output_dir else pathlib.Path(repo_path)
    rundir = out / ".axiom" / "runs" / ts / skill_id
    rundir.mkdir(parents=True, exist_ok=True)
    # Deterministic report: checklist + findings skeleton from skill body headings
    report = (f"# Run report: {skill_id} v{fm.get('version')} ({ts})\n\n"
              f"Objective: {objective or '(none stated)'}\n\n"
              f"Targets: {', '.join(targets) or '(none)'}\n\n"
              f"Tools selected: {', '.join(tools) or '(none)'}\n\n"
              f"## Findings\n- (no automated findings in scaffold run; "
              f"extend per-skill scripts)\n\n"
              f"## Next actions\n- Review checklist in skills/{skill_id}/checklists/\n")
    # Run shipped checker scripts (repo-confined, no shell injection).
    import subprocess as _sp
    checker_outputs: list[str] = []
    checker_rc = 0
    for c in checkers:
        try:
            proc = _sp.run([sys.executable, str(c), str(pathlib.Path(repo_path).resolve())],
                           capture_output=True, text=True, timeout=120)
            checker_rc = max(checker_rc, proc.returncode)
            checker_outputs.append(f"### {c.name}\n```\n{proc.stdout.strip()}\n```\n"
                                  + (f"stderr:\n```\n{proc.stderr.strip()}\n```\n" if proc.stderr.strip() else ""))
        except Exception as exc:  # noqa: BLE001
            checker_outputs.append(f"### {c.name}\nERROR: {exc}\n")
            checker_rc = max(checker_rc, 1)
    if checker_outputs:
        report += "\n## Checker results\n\n" + "\n".join(checker_outputs)
        manifest["decisions"].append(f"ran {len(checkers)} checker(s), rc={checker_rc}")
    (rundir / "report.md").write_text(report, encoding="utf-8")
    (rundir / "run-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["generated_files"] = [str(rundir / "report.md"),
                                   str(rundir / "run-manifest.json")]
    manifest["acceptance_checks"] = ["report.md written", "run-manifest.json written"]
    if checkers:
        manifest["acceptance_checks"].append(f"checkers rc={checker_rc}")
    status = "ok" if checker_rc == 0 else "failed-checks"
    return {"status": status, "manifest": manifest, "run_dir": str(rundir),
            "checker_rc": checker_rc,
            "summary": f"{skill_id}: wrote 2 files to {rundir} (rc={checker_rc})"}
