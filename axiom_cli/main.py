from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import yaml

from packages.context.indexer import write_index
from packages.context.selector import select_from_index, ContextBudget
from packages.workflow.entry import starting_phase
from packages.workflow.engine import load as load_workflow
from packages.agents.router import route
from packages.skills.engage import engage
from packages.axiom_ops import get_status, plan_fix, plan_feature
from packages.axiom_mcp.server import serve as mcp_serve
from packages.axiom_server.server import serve as http_serve

ROOT = pathlib.Path(__file__).resolve().parents[1]

def _read_yaml(path: str | pathlib.Path):
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")) or {}

def validate_repo() -> int:
    required = [ROOT/"AGENTS.md", ROOT/"schemas", ROOT/"profiles", ROOT/"skills", ROOT/"workflows", ROOT/"packages"]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    forbidden = [ROOT/"legacy"]
    present_forbidden = [str(p.relative_to(ROOT)) for p in forbidden if p.exists()]
    if missing or present_forbidden:
        print("Repository validation: FAIL")
        if missing:
            print("Missing:", *missing, sep="\n")
        if present_forbidden:
            print("Forbidden vendored trees:", *present_forbidden, sep="\n")
        return 1
    print("Repository validation: PASS")
    return 0

def validate_profile(path: str) -> int:
    data = _read_yaml(path)
    required = ["id", "version", "domains", "capabilities"]
    missing = [k for k in required if k not in data]
    if missing:
        print("Profile validation: FAIL")
        if missing:
            print("Missing:", *missing, sep="\n")
        if present_forbidden:
            print("Forbidden vendored trees:", *present_forbidden, sep="\n")
        return 1
    print(json.dumps(data, indent=2))
    return 0

def doctor() -> int:
    checks = []
    checks.append(("python", sys.version.split()[0]))
    checks.append(("repo", "PASS" if validate_repo() == 0 else "FAIL"))
    try:
        subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        checks.append(("tests", "PASS"))
    except Exception:
        checks.append(("tests", "NOT_RUN_OR_FAIL"))
    print("AxiomEmbedded doctor")
    for name, value in checks:
        print(f"- {name}: {value}")
    return 0 if all(v not in {"FAIL"} for _, v in checks) else 1

def analyze(path: str) -> int:
    target = pathlib.Path(path).resolve()
    output = target/".axiom"/"index.json"
    count = write_index(target, output)
    print(json.dumps({"root": str(target), "files_indexed": count, "index": str(output)}, indent=2))
    return 0

def graph_build(path: str, output: str | None) -> int:
    target = pathlib.Path(path).resolve()
    out = pathlib.Path(output).resolve() if output else target/".axiom"/"index.json"
    count = write_index(target, out)
    print(f"Graph/index written: {out} ({count} files)")
    return 0

def context_select(index: str, roots: list[str], hops: int, max_files: int, max_bytes: int) -> int:
    selected = select_from_index(index, roots, ContextBudget(max_files=max_files, max_bytes=max_bytes))
    print(json.dumps({"roots": roots, "hops": hops, "selected": selected}, indent=2))
    return 0

def impact(path: str) -> int:
    p = pathlib.Path(path)
    data = _read_yaml(p) if p.suffix in {".yaml", ".yml"} else {}
    print(json.dumps({"project": data.get("id", p.stem), "mode": data.get("lifecycle", "unknown"), "entry": data.get("entry", "unknown"), "next_phase": starting_phase(data.get("entry", "brownfield"))}, indent=2))
    return 0

def workflow_plan(profile: str, entry: str | None) -> int:
    data = _read_yaml(profile)
    mode = entry or data.get("entry", "greenfield")
    print(json.dumps({"profile": data.get("id"), "entry": mode, "start_phase": starting_phase(mode), "lifecycle": data.get("lifecycle", "v-model")}, indent=2))
    return 0

def engage_cmd(domain: str | None, platform: str | None) -> int:
    print(json.dumps(engage(domain, platform), indent=2))
    return 0

def run_cmd(request: str, domain: str | None, platform: str | None) -> int:
    """Opencode-like standalone run: engage skills, route intent, emit a plan-then-execute plan.

    The host harness (Claude Code, OpenCode, Codex, Antigravity) provides the model;
    axiom resolves WHAT to load and in WHAT order. Execution beyond planning
    requires human approval per configs/project.yaml.
    """
    selection = engage(domain, platform)
    plan = {
        "mode": "plan-then-execute",
        "request": request,
        "intent": route(request),
        "engagement": selection,
        "phases": ["plan", "implement", "verify", "evidence"],
        "context_files": selection["context_files"],
        "approval_required_for": ["git push", "release", "destructive_command", "safety_critical_change", "security_critical_change"],
    }
    print(json.dumps(plan, indent=2))
    return 0

def status_cmd(format: str) -> int:
    st = get_status()
    if format == "json":
        print(json.dumps(st, indent=2))
        return 0
    bar = lambda n, total: "#" * int(20 * n / total) + "-" * (20 - int(20 * n / total)) if total else "-" * 20
    print(f"\nAXIOMEMBEDDED - {st['project']} [{st['state'].upper()}]")
    print(f"Skills: {st['skills']['total']} at v{st['skills']['latest']}  {bar(st['skills']['total'] - len(st['skills']['stale']), st['skills']['total'])}")
    for key, val in st["inventory"].items():
        print(f"  {key:12s} {val}")
    print("\nNEEDS ATTENTION")
    if st["needs_attention"]:
        for a in st["needs_attention"]:
            print(f"  [{a['severity'].upper()}] {a['id']}: {a['title']}")
    else:
        print("  None — all systems nominal.")
    print(f"\nRECOMMENDED: {st['recommended_next_action']}")
    return 0


def fix_cmd(issue_id: str, domain: str | None, platform: str | None) -> int:
    print(json.dumps(plan_fix(issue_id, domain, platform), indent=2))
    return 0


def feature_cmd(feature_id: str, domain: str | None, platform: str | None) -> int:
    print(json.dumps(plan_feature(feature_id, domain, platform), indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="axiom", description="AxiomEmbedded engineering CLI")
    sp = ap.add_subparsers(dest="cmd")
    sp.add_parser("doctor")
    sp.add_parser("repo-validate")
    repo = sp.add_parser("repo"); repo.add_argument("action", choices=["validate"])
    prof = sp.add_parser("profile"); prof_sub = prof.add_subparsers(dest="profile_cmd"); pv = prof_sub.add_parser("validate"); pv.add_argument("path")
    an = sp.add_parser("analyze"); an.add_argument("path", nargs="?", default=".")
    graph = sp.add_parser("graph"); gs = graph.add_subparsers(dest="graph_cmd"); gb = gs.add_parser("build"); gb.add_argument("path", nargs="?", default="."); gb.add_argument("--output")
    ctx = sp.add_parser("context"); cs = ctx.add_subparsers(dest="context_cmd"); cc = cs.add_parser("select"); cc.add_argument("--index", default=".axiom/index.json"); cc.add_argument("--root", action="append", required=True); cc.add_argument("--hops", type=int, default=2); cc.add_argument("--max-files", type=int, default=24); cc.add_argument("--max-bytes", type=int, default=500000)
    im = sp.add_parser("impact"); im.add_argument("path")
    wf = sp.add_parser("workflow"); ws = wf.add_subparsers(dest="workflow_cmd"); wp = ws.add_parser("plan"); wp.add_argument("--profile", required=True); wp.add_argument("--entry")
    rt = sp.add_parser("route"); rt.add_argument("request")
    en = sp.add_parser("engage"); en.add_argument("--domain"); en.add_argument("--platform")
    rn = sp.add_parser("run"); rn.add_argument("request"); rn.add_argument("--domain"); rn.add_argument("--platform")
    st = sp.add_parser("status", help="Terminal dashboard: project health + next action"); st.add_argument("--format", choices=["text", "json"], default="text")
    fx = sp.add_parser("fix", help="Emit the 10-step fix-defect plan for an issue id"); fx.add_argument("issue_id"); fx.add_argument("--domain"); fx.add_argument("--platform")
    ft = sp.add_parser("feature", help="Emit the 9-step add-feature plan for a feature id"); ft.add_argument("feature_id"); ft.add_argument("--domain"); ft.add_argument("--platform")
    sp.add_parser("mcp", help="Serve Model Context Protocol over stdio (any MCP client)")
    sv = sp.add_parser("serve", help="Serve REST + A2A over HTTP (web apps, custom AI, local LLMs)"); sv.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    if args.cmd == "doctor": return doctor()
    if args.cmd == "repo-validate": return validate_repo()
    if args.cmd == "repo": return validate_repo()
    if args.cmd == "profile" and args.profile_cmd == "validate": return validate_profile(args.path)
    if args.cmd == "analyze": return analyze(args.path)
    if args.cmd == "graph" and args.graph_cmd == "build": return graph_build(args.path, args.output)
    if args.cmd == "context" and args.context_cmd == "select": return context_select(args.index, args.root, args.hops, args.max_files, args.max_bytes)
    if args.cmd == "impact": return impact(args.path)
    if args.cmd == "workflow" and args.workflow_cmd == "plan": return workflow_plan(args.profile, args.entry)
    if args.cmd == "route": print(route(args.request)); return 0
    if args.cmd == "engage": return engage_cmd(args.domain, args.platform)
    if args.cmd == "run": return run_cmd(args.request, args.domain, args.platform)
    if args.cmd == "status": return status_cmd(args.format)
    if args.cmd == "fix": return fix_cmd(args.issue_id, args.domain, args.platform)
    if args.cmd == "feature": return feature_cmd(args.feature_id, args.domain, args.platform)
    if args.cmd == "mcp": return mcp_serve()
    if args.cmd == "serve": return http_serve(args.port)
    ap.print_help(); return 0

if __name__ == "__main__":
    raise SystemExit(main())
