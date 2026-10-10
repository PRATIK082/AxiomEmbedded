from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import yaml

from axiom_cli import __version__ as CLI_VERSION

from packages.context.indexer import write_index
from packages.context.selector import select_from_index, ContextBudget
from packages.workflow.entry import starting_phase
from packages.workflow.stage import detect_stage, reconcile_stage
from packages.workflow.engine import load as load_workflow
from packages.agents.router import route, detect_domain
from packages.skills.engage import engage
from packages.axiom_ops import get_status, plan_fix, plan_feature
from packages.launcher import execute as oc_execute, opencode_status, RESEARCH_PREAMBLE
from axiom_mcp.server import serve as mcp_serve
from packages.axiom_server.server import serve as http_serve

ROOT = pathlib.Path(__file__).resolve().parents[1]

def _read_yaml(path: str | pathlib.Path):
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")) or {}

def is_source_checkout() -> bool:
    """True when ROOT looks like a source checkout (content trees live there)."""
    return (ROOT / "pyproject.toml").exists() or (ROOT / ".git").exists()

def validate_repo() -> int:
    if not is_source_checkout():
        # Installed distribution (pip/pipx): only code ships, so content-tree
        # checks do not apply. Report SKIP instead of a misleading FAIL.
        print("Repository validation: SKIP (installed distribution, not a source checkout)")
        return 0
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
        print("Missing:", *missing, sep="\n")
        return 1
    print(json.dumps(data, indent=2))
    return 0

def get_version() -> str:
    """Installed distribution version, falling back to the source tree marker."""
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("axiom-embedded")
        except PackageNotFoundError:
            return CLI_VERSION
    except Exception:
        return CLI_VERSION

def version_cmd() -> int:
    print(get_version())
    return 0

def doctor(skip_tests: bool = False) -> int:
    results: list[tuple[str, str, bool]] = []
    py = sys.version.split()[0]
    py_ok = sys.version_info >= (3, 11)
    results.append(("python", py, py_ok))
    results.append(("axiom", get_version(), True))
    try:
        import yaml as _yaml  # noqa: F401
        results.append(("pyyaml", getattr(_yaml, "__version__", "installed"), True))
    except Exception as exc:
        results.append(("pyyaml", f"MISSING ({exc})", False))
    on_path = shutil.which("axiom") is not None
    # When invoked as `python -m axiom_cli`, the shim may legitimately be absent
    # (e.g. uninstalled source tree); report it without failing doctor.
    results.append(("axiom_on_path", shutil.which("axiom") or "not-found (use pipx install .)", True))
    oc = opencode_status()
    # Missing opencode only disables the `axiom oc` launcher (non-fatal note);
    # any detected-but-unusable binary (untested major, broken version)
    # fails doctor closed (see docs/OPENCODE_COMPAT.md).
    oc_ok = oc["state"] in ("ok", "warn") or oc["binary"] is None
    results.append(("opencode", f"{oc.get('version') or 'not-found'} [{oc['state']}] {oc['detail']}", oc_ok))
    repo_ok = validate_repo() == 0
    repo_label = ("PASS" if repo_ok else "FAIL") if is_source_checkout() else "SKIP (installed package)"
    results.append(("repo", repo_label, repo_ok))
    if skip_tests:
        results.append(("tests", "SKIPPED (--skip-tests)", True))
    else:
        try:
            subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            results.append(("tests", "PASS", True))
        except Exception:
            results.append(("tests", "NOT_RUN_OR_FAIL (run python -m pytest -q)", True))
    print("AxiomEmbedded doctor")
    for name, value, _ok in results:
        print(f"- {name}: {value}")
    # Non-fatal notes (tests, shim presence) never fail doctor; only hard
    # requirements (python, deps, repo) determine the exit code.
    hard_ok = py_ok and repo_ok and results[2][2] and oc_ok
    _ = on_path
    return 0 if hard_ok else 1

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

def engage_cmd(domain: str | None, platform: str | None, group: str | None = None,
               limit: int = 0) -> int:
    print(json.dumps(engage(domain, platform, group, limit), indent=2))
    return 0


def packs_cmd(domain: str | None, platform: str | None, standards: list[str]) -> int:
    from packages.toolpacks.select import select_packs

    print(json.dumps(select_packs(domain, platform, standards), indent=2))
    return 0


def compose_cmd(prompt: str, domain: str | None, platform: str | None,
                os: str | None, language: str | None, standards: list[str],
                hardware: str | None, technology: str | None) -> int:
    from packages.compose.mindmap import compose_mindmap

    print(json.dumps(compose_mindmap(prompt, domain, platform, os, language,
                                     standards, hardware, technology), indent=2))
    return 0


def packs_cmd(domain: str | None, platform: str | None, standards: list[str]) -> int:
    from packages.toolpacks.select import select_packs

    print(json.dumps(select_packs(domain, platform, standards), indent=2))
    return 0

def run_cmd(request: str, domain: str | None, platform: str | None) -> int:
    """Opencode-like standalone run: engage skills, route intent, emit a plan-then-execute plan.

    The host harness (Claude Code, OpenCode, Codex, Antigravity) provides the model;
    axiom resolves WHAT to load and in WHAT order. Execution beyond planning
    requires human approval per configs/project.yaml.
    """
    selection = None
    domain_source = "explicit"
    if not domain:
        domain = detect_domain(request)
        domain_source = "detected" if domain else "none"
    selection = engage(domain, platform)
    plan = {
        "mode": "plan-then-execute",
        "request": request,
        "intent": route(request),
        "domain_source": domain_source,
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


def stage_cmd(path: str, profile: str | None) -> int:
    """Evidence-based stage: deepest V-Model phase with artifacts on disk,
    reconciled with the profile's declared entry (declaration wins)."""
    detected = detect_stage(path)
    declared_phase = None
    if profile:
        data = _read_yaml(profile)
        declared_phase = starting_phase(data.get("entry", "brownfield"))
    print(json.dumps({
        "path": str(pathlib.Path(path).resolve()),
        "profile": profile,
        **reconcile_stage(detected["stage"], declared_phase),
        "evidence": detected["evidence"],
    }, indent=2))
    return 0


def fix_cmd(issue_id: str, domain: str | None, platform: str | None) -> int:
    print(json.dumps(plan_fix(issue_id, domain, platform), indent=2))
    return 0


def feature_cmd(feature_id: str, domain: str | None, platform: str | None) -> int:
    print(json.dumps(plan_feature(feature_id, domain, platform), indent=2))
    return 0


def research_cmd(question: str, backend: str = "auto", max_subquestions: int = 3,
                 fmt: str = "json", output: str | None = None,
                 model: str | None = None) -> int:
    """Deep-research pipeline (Phase 3); auto falls back to local on no binary."""
    from packages.research import BACKENDS, DEFAULT_MAX_SUBQUESTIONS, run

    if backend not in BACKENDS:
        print(json.dumps({"status": "error",
                          "message": f"unknown backend: {backend} (choose from {BACKENDS})"},
                         indent=2))
        return 1
    envelope = run(question, backend=backend,
                   max_subquestions=max_subquestions or DEFAULT_MAX_SUBQUESTIONS,
                   model=model)
    if output:
        import pathlib as _pl

        _pl.Path(output).write_text(envelope.get("report", ""), encoding="utf-8")
    if fmt == "markdown":
        print(envelope.get("report", ""))
    else:
        print(json.dumps(envelope, indent=2))
    return 0 if envelope.get("status") == "ok" else 1


def install_cmd(client: str, global_install: bool, path: str, source: str | None, home: str | None,
                domains: list[str] | None = None, groups: list[str] | None = None) -> int:
    import pathlib as _pl
    from packages.installer import find_content_source, install_client

    try:
        content = find_content_source(source)
    except ValueError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
        return 1
    result = install_client(
        client,
        _pl.Path(path).resolve(),
        _pl.Path(home).expanduser() if home else _pl.Path.home(),
        content,
        is_global=global_install,
        domains=domains,
        groups=groups,
    )
    print(json.dumps({"status": "ok", **result}, indent=2))
    return 0


def _csv(value: str | None) -> list[str] | None:
    return [d.strip() for d in (value or "").split(",") if d.strip()] or None


def uninstall_cmd(client: str, global_install: bool, path: str, home: str | None) -> int:
    import pathlib as _pl
    from packages.installer import uninstall_client

    result = uninstall_client(
        client,
        _pl.Path(path).resolve(),
        _pl.Path(home).expanduser() if home else _pl.Path.home(),
        is_global=global_install,
    )
    print(json.dumps({"status": "ok", **result}, indent=2))
    return 0


def update_cmd(client: str, global_install: bool, path: str, source: str | None,
               home: str | None, domains: list[str] | None = None,
               groups: list[str] | None = None) -> int:
    import pathlib as _pl
    from packages.installer import find_content_source, update_client

    try:
        content = find_content_source(source)
    except ValueError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
        return 1
    result = update_client(
        client,
        _pl.Path(path).resolve(),
        _pl.Path(home).expanduser() if home else _pl.Path.home(),
        content,
        is_global=global_install,
        domains=domains,
        groups=groups,
    )
    print(json.dumps({"status": "ok", **result}, indent=2))
    return 0


def oc_cmd(verb: str, args: list[str], model: str | None, agent: str | None,
           directory: str | None, fmt: str | None, title: str | None,
           source: str | None, isolate: bool, dry_run: bool) -> int:
    if verb == "research" and not agent:
        # Read-only framing by default; Phase 3 adds dedicated subagents.
        agent = "explore"
        args = [RESEARCH_PREAMBLE + " ".join(args)] if args else [RESEARCH_PREAMBLE]
    return oc_execute(verb, args, model=model, agent=agent, directory=directory,
                      fmt=fmt, title=title, source=source, isolate=isolate, dry_run=dry_run)


def skills_cmd(action: str, args: argparse.Namespace) -> int:
    from packages import axiom_sdk

    if action == "list":
        import yaml as _yaml
        cat = _yaml.safe_load(
            (ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
        for e in cat.get("skills", []):
            print(f"{e['id']} [{e.get('maturity', '?')}] {e.get('title', '')}")
        return 0
    if action == "validate":
        from packages.skills.validator import validate_all
        rep = validate_all()
        bad = [r for r in rep["skills"] if not r["valid"]]
        print(json.dumps({"valid": rep["valid"],
                          "failures": [r["skill"] for r in bad]}, indent=2))
        return 0 if rep["valid"] else 1
    if action == "search":
        print(json.dumps(axiom_sdk.search_skills(
            getattr(args, "query", "") or "",
            getattr(args, "domain", None)), indent=2))
        return 0
    if action == "run":
        print(json.dumps(axiom_sdk.run_skill(
            args.skill_id, getattr(args, "repo", "."),
            (getattr(args, "target", None) or []),
            getattr(args, "objective", "") or "",
            getattr(args, "constraints", "") or "",
            getattr(args, "output", None),
            not getattr(args, "apply", False)), indent=2))
        return 0
    if action == "report":
        print(json.dumps(axiom_sdk.skill_report(
            args.skill_id, args.run_dir), indent=2))
        return 0
    if action == "manifest":
        print(json.dumps(axiom_sdk.skill_manifest(args.skill_id), indent=2))
        return 0
    if action == "create":
        from scripts.create_skill import scaffold
        plan = scaffold(args.skill_id, args.title,
                        getattr(args, "domain", "automotive") or "automotive",
                        bool(getattr(args, "apply", False)))
        print(json.dumps({"skill": args.skill_id, "files": plan,
                          "applied": bool(getattr(args, "apply", False))},
                         indent=2))
        return 0
    if action == "apply":
        from scripts.skill_pipeline import run_pipeline
        rep = run_pipeline(check=bool(getattr(args, "check", False)))
        print(json.dumps(rep, indent=2))
        return 0 if rep["status"] == "ok" else 1
    if action == "link":
        from packages.skills.registry import set_link
        try:
            res = set_link(args.kind, args.skill_id, args.values or [])
        except ValueError as exc:
            print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
            return 1
        print(json.dumps({"status": "ok", **res}, indent=2))
        return 0
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="axiom", description="AxiomEmbedded engineering CLI")
    ap.add_argument("--version", action="store_true", help="Print the axiom version and exit")
    sp = ap.add_subparsers(dest="cmd")
    sp.add_parser("version", help="Print the axiom version")
    sp.add_parser("doctor").add_argument("--skip-tests", action="store_true", help="Skip the pytest health check")
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
    pk = sp.add_parser("packs", help="Select plug-and-play tool/pip packs by domain+platform+standards"); pk.add_argument("--domain"); pk.add_argument("--platform"); pk.add_argument("--standard", dest="standards", action="append", default=[], help="Repeatable standard filter (e.g. --standard 'ISO 14229-1')")
    rn = sp.add_parser("run"); rn.add_argument("request"); rn.add_argument("--domain"); rn.add_argument("--platform")
    st = sp.add_parser("status", help="Terminal dashboard: project health + next action"); st.add_argument("--format", choices=["text", "json"], default="text")
    fx = sp.add_parser("fix", help="Emit the 10-step fix-defect plan for an issue id"); fx.add_argument("issue_id"); fx.add_argument("--domain"); fx.add_argument("--platform")
    ft = sp.add_parser("feature", help="Emit the 9-step add-feature plan for a feature id"); ft.add_argument("feature_id"); ft.add_argument("--domain"); ft.add_argument("--platform")
    rs = sp.add_parser("research", help="Deep-research pipeline (planner -> searchers -> verifier -> synthesizer)"); rs.add_argument("question")
    rs.add_argument("--backend", default="auto",
                    choices=["auto", "opencode", "local", "tavily", "brave", "searxng"],
                    help="Searcher backend (auto: opencode subagents, else local fallback)")
    rs.add_argument("--max-subquestions", type=int, default=3)
    rs.add_argument("--format", choices=["json", "markdown"], default="json")
    rs.add_argument("--output", default=None, help="Write the markdown report to FILE")
    rs.add_argument("--model", default=None, help="Model id for the opencode backend")
    ins = sp.add_parser("install", help="Install the Axiom pack into a project or user-global config")
    ins.add_argument("--client", required=True, choices=["opencode", "claude", "codex", "gemini", "copilot",
                                                         "cursor", "cline", "aider", "kilo", "openhands"])
    ins.add_argument("--global", dest="global_install", action="store_true", help="Install to user-global config instead of a project dir")
    ins.add_argument("--path", default=".", help="Target project dir (project scope; default: cwd)")
    ins.add_argument("--source", default=None, help="Axiom content source dir (default: auto-detect checkout)")
    ins.add_argument("--home", default=None, help="Override home dir (testing global installs)")
    ins.add_argument("--domains", default=None,
                     help="Comma-separated domain filter for copied skills (e.g. automotive,robotics). "
                          "Skills with domains=[all] are always included. MCP discovery filters at runtime via engage().")
    ins.add_argument("--groups", default=None,
                     help="Comma-separated skill-group filter from skills/groups.yaml "
                          "(e.g. diagnostics,testing-verification). Combines with --domains (AND).")
    uns = sp.add_parser("uninstall", help="Remove the Axiom pack (MCP entry, generated files); never touches user content")
    uns.add_argument("--client", required=True, choices=["opencode", "claude", "codex", "gemini", "copilot",
                                                         "cursor", "cline", "aider", "kilo", "openhands"])
    uns.add_argument("--global", dest="global_install", action="store_true")
    uns.add_argument("--path", default=".")
    uns.add_argument("--home", default=None, help="Override home dir (testing global installs)")
    upd = sp.add_parser("update", help="Refresh the Axiom pack (re-install + report stale/force-refreshed files)")
    upd.add_argument("--client", required=True, choices=["opencode", "claude", "codex", "gemini", "copilot",
                                                         "cursor", "cline", "aider", "kilo", "openhands"])
    upd.add_argument("--global", dest="global_install", action="store_true")
    upd.add_argument("--path", default=".")
    upd.add_argument("--source", default=None)
    upd.add_argument("--home", default=None, help="Override home dir (testing global installs)")
    upd.add_argument("--domains", default=None)
    upd.add_argument("--groups", default=None,
                     help="Comma-separated skill-group filter from skills/groups.yaml.")
    oc = sp.add_parser("oc", help="Launch OpenCode with an Axiom-isolated config (Phase 2)")
    oc_sub = oc.add_subparsers(dest="oc_cmd", required=True)
    for verb in ("tui", "run", "research"):
        p = oc_sub.add_parser(verb, help=f"opencode {verb} via the axiom launcher")
        if verb in ("run", "research"):
            p.add_argument("prompt", nargs="*", help="Message/question for the session")
        if verb == "run":
            p.add_argument("--format", choices=["default", "json"], default=None)
            p.add_argument("--title", default=None)
        p.add_argument("--model", default=None, help="Model id passed through to opencode (provider/model)")
        p.add_argument("--agent", default=None, help="OpenCode agent (tui/run) — research defaults to explore")
        p.add_argument("--dir", default=None, help="Project directory for the session")
        p.add_argument("--source", default=None, help="Axiom content source dir (default: auto-detect checkout)")
        p.add_argument("--no-isolate", dest="isolate", action="store_false",
                       help="Use the operator's own OpenCode config instead of the Axiom-isolated one")
        p.add_argument("--dry-run", action="store_true",
                       help="Print the resolved argv/env/config without executing")
    mc = sp.add_parser("mcp", help="Serve Model Context Protocol over stdio (any MCP client)")
    mc.add_argument("--check", action="store_true", help="Run the MCP handshake + tool-inventory compat probe instead of serving")
    sg = sp.add_parser("stage", help="Detect project lifecycle stage from evidence + profile entry")
    sg.add_argument("path", nargs="?", default="."); sg.add_argument("--profile")
    sk = sp.add_parser("skills", help="Skill framework: list/validate/search/run/report/create/apply")
    sk_sub = sk.add_subparsers(dest="skills_cmd", required=True)
    sk_sub.add_parser("list", help="List catalog skills")
    sk_sub.add_parser("validate", help="Validate all skills + catalog")
    ss = sk_sub.add_parser("search", help="Search catalog skills")
    ss.add_argument("query", nargs="?", default=""); ss.add_argument("--domain")
    sr = sk_sub.add_parser("run", help="Run a skill (dry-run unless --apply)")
    sr.add_argument("skill_id"); sr.add_argument("--repo", default=".")
    sr.add_argument("--target", action="append", default=[])
    sr.add_argument("--objective", default=""); sr.add_argument("--constraints", default="")
    sr.add_argument("--output", default=None); sr.add_argument("--apply", action="store_true")
    sp_ = sk_sub.add_parser("report", help="Summarize a run manifest dir")
    sp_.add_argument("skill_id"); sp_.add_argument("run_dir")
    sm = sk_sub.add_parser("manifest", help="Print derived manifest.json for a skill")
    sm.add_argument("skill_id")
    sc = sk_sub.add_parser("create", help="Scaffold a skill (dry-run unless --apply)")
    sc.add_argument("skill_id"); sc.add_argument("--title", required=True)
    sc.add_argument("--domain", default="automotive"); sc.add_argument("--apply", action="store_true")
    sa = sk_sub.add_parser("apply", help="Run the full skill pipeline: enrich->index->clients->validate")
    sa.add_argument("--check", action="store_true", help="Verify only; exit 1 if generated files are stale")
    sl = sk_sub.add_parser("link", help="Edit the skill graph in catalog.yaml (single source; then run skills apply)")
    sl.add_argument("--set", dest="op", action="store_const", const="set", required=True)
    sl.add_argument("kind", choices=["related_skills", "extends", "sub_skills", "domain_overlays", "platform_overlays"])
    sl.add_argument("skill_id"); sl.add_argument("values", nargs="*")
    sv = sp.add_parser("serve", help="Serve REST + A2A over HTTP (web apps, custom AI, local LLMs)"); sv.add_argument("--port", type=int, default=8765)
    ar = sp.add_parser("artifact", help="Validate assurance artifacts against schemas"); ar_sub = ar.add_subparsers(dest="artifact_cmd", required=True)
    ar_v = ar_sub.add_parser("validate", help="Validate one artifact file"); ar_v.add_argument("path")
    tr = sp.add_parser("trace", help="Traceability checks over an artifact directory"); tr_sub = tr.add_subparsers(dest="trace_cmd", required=True)
    tr_c = tr_sub.add_parser("check", help="Check cross-artifact traceability"); tr_c.add_argument("path", nargs="?", default=".")
    rv = sp.add_parser("review", help="Validate review reports"); rv_sub = rv.add_subparsers(dest="review_cmd", required=True)
    rv_c = rv_sub.add_parser("check", help="Validate one review report file"); rv_c.add_argument("path")
    args = ap.parse_args()
    if args.version: return version_cmd()
    if args.cmd == "version": return version_cmd()
    if args.cmd == "doctor": return doctor(skip_tests=getattr(args, "skip_tests", False))
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
    if args.cmd == "packs": return packs_cmd(args.domain, args.platform, args.standards or [])
    if args.cmd == "run": return run_cmd(args.request, args.domain, args.platform)
    if args.cmd == "status": return status_cmd(args.format)
    if args.cmd == "fix": return fix_cmd(args.issue_id, args.domain, args.platform)
    if args.cmd == "feature": return feature_cmd(args.feature_id, args.domain, args.platform)
    if args.cmd == "research": return research_cmd(args.question, args.backend, args.max_subquestions, args.format, args.output, args.model)
    if args.cmd == "install": return install_cmd(args.client, args.global_install, args.path, args.source, args.home,
                                         _csv(args.domains), _csv(args.groups))
    if args.cmd == "uninstall": return uninstall_cmd(args.client, args.global_install, args.path, args.home)
    if args.cmd == "update": return update_cmd(args.client, args.global_install, args.path, args.source, args.home,
                                         _csv(args.domains), _csv(args.groups))
    if args.cmd == "oc":
        return oc_cmd(args.oc_cmd, getattr(args, "prompt", None) or [], args.model, args.agent, args.dir,
                      getattr(args, "format", None), getattr(args, "title", None),
                      args.source, args.isolate, args.dry_run)
    if args.cmd == "mcp":
        if getattr(args, "check", False):
            from axiom_mcp.server import check as mcp_check
            report = mcp_check()
            print(json.dumps(report, indent=2))
            return 0 if report.get("status") == "ok" else 1
        return mcp_serve()
    if args.cmd == "stage": return stage_cmd(args.path, args.profile)
    if args.cmd == "skills": return skills_cmd(args.skills_cmd, args)
    if args.cmd == "artifact" and args.artifact_cmd == "validate":
        from packages.skills.assurance import validate_artifact_file
        print(json.dumps(validate_artifact_file(args.path), indent=2))
        return 0 if validate_artifact_file(args.path)["valid"] else 1
    if args.cmd == "trace" and args.trace_cmd == "check":
        from packages.skills.assurance import check_traceability
        rep = check_traceability(args.path)
        print(json.dumps(rep, indent=2))
        return 0 if rep["valid"] else 1
    if args.cmd == "review" and args.review_cmd == "check":
        from packages.skills.assurance import validate_artifact_file
        rep = validate_artifact_file(args.path)
        print(json.dumps(rep, indent=2))
        return 0 if rep["valid"] and rep.get("kind") == "review-report" else 1
    if args.cmd == "serve": return http_serve(args.port)
    ap.print_help(); return 0

if __name__ == "__main__":
    raise SystemExit(main())
