"""Skill runner: structured dry-run + manifest-producing execution (no shell, no net)."""
from __future__ import annotations
import datetime
import json
import pathlib
import re

from packages.skills.loader import load_skill

ROOT = pathlib.Path(__file__).resolve().parents[2]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _safe_rel(p: str) -> pathlib.Path:
    pp = pathlib.Path(p)
    if pp.is_absolute() or ".." in pp.parts:
        raise ValueError(f"unsafe path: {p!r}")
    return pp


def run_skill(skill_id: str, repo_path: str = ".", target_files: list[str] | None = None,
              objective: str = "", constraints: str = "",
              output_dir: str | None = None, dry_run: bool = True) -> dict:
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
    manifest = {
        "skill": skill_id,
        "version": str(fm.get("version")),
        "timestamp": ts,
        "inputs": {"repo_path": repo_path, "target_files": targets,
                   "objective": objective, "constraints": constraints},
        "selected_tools": tools,
        "decisions": [f"loaded skill {skill_id} v{fm.get('version')}",
                      f"dry_run={dry_run}"],
        "generated_files": [],
        "warnings": [],
        "acceptance_checks": ["SKILL.md sections present",
                              f"dry-run={dry_run} => no writes" if dry_run
                              else "artifacts written under output dir"],
    }
    if dry_run:
        manifest["decisions"].append(
            f"would write run manifest to .axiom/runs/{ts}/{skill_id}/run-manifest.json")
        return {"status": "dry-run", "manifest": manifest,
                "summary": f"{skill_id}: dry-run OK, {len(targets)} target(s), "
                           f"{len(tools)} tool(s) selected"}
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
    (rundir / "report.md").write_text(report, encoding="utf-8")
    (rundir / "run-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["generated_files"] = [str(rundir / "report.md"),
                                   str(rundir / "run-manifest.json")]
    manifest["acceptance_checks"] = ["report.md written", "run-manifest.json written"]
    return {"status": "ok", "manifest": manifest, "run_dir": str(rundir),
            "summary": f"{skill_id}: wrote 2 files to {rundir}"}
