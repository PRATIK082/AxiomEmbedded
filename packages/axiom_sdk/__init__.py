"""AxiomEmbedded Python SDK — single implementation behind every interface.

All other surfaces (MCP server, REST/A2A server, CLI additions) delegate to
these functions so SDK/CLI/MCP/REST/A2A always agree. Stdlib + PyYAML only.
"""

from __future__ import annotations

import pathlib

from packages.agents.router import route, detect_domain
from packages.skills.engage import engage
from packages.toolpacks.select import select_packs

ROOT = pathlib.Path(__file__).resolve().parents[2]

APPROVAL_REQUIRED_FOR = [
    "git push",
    "release",
    "destructive_command",
    "safety_critical_change",
    "security_critical_change",
]


def engage_skills(domain: str | None = None, platform: str | None = None) -> dict:
    """Resolve which skills/profiles a domain+platform project needs."""
    return engage(domain, platform)


def select_toolpacks(
    domain: str | None = None,
    platform: str | None = None,
    standards: list[str] | None = None,
) -> dict:
    """Resolve which tools/pip packs/agents a domain+platform+standards project needs."""
    return select_packs(domain, platform, standards)


def compose_mindmap(
    prompt: str,
    domain: str | None = None,
    platform: str | None = None,
    os: str | None = None,
    language: str | None = None,
    standards: list[str] | None = None,
    hardware: str | None = None,
    technology: str | None = None,
) -> dict:
    """Compose a skill mind-map DAG from a prompt + facet axes."""
    from packages.compose.mindmap import compose_mindmap as _compose

    return _compose(prompt, domain, platform, os, language, standards,
                    hardware, technology)


def run_plan(request: str, domain: str | None = None, platform: str | None = None) -> dict:
    """Opencode-like plan: engagement + routed intent + phased execution plan.

    The host harness supplies the model; axiom resolves WHAT to load and in
    WHAT order. Execution beyond planning requires human approval.
    """
    selection = None
    domain_source = "explicit"
    if not domain:
        domain = detect_domain(request)
        domain_source = "detected" if domain else "none"
    selection = engage(domain, platform)
    return {
        "mode": "plan-then-execute",
        "request": request,
        "intent": route(request),
        "domain_source": domain_source,
        "engagement": selection,
        "phases": ["plan", "implement", "verify", "evidence"],
        "context_files": selection["context_files"],
        "approval_required_for": APPROVAL_REQUIRED_FOR,
    }


def read_skill(skill_id: str) -> dict:
    """Return a skill's SKILL.md body plus its manifest and facet metadata."""
    import yaml

    skill_dir = ROOT / "skills" / skill_id
    body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    manifest = yaml.safe_load((skill_dir / "manifest.yaml").read_text(encoding="utf-8"))
    return {"id": skill_id, "manifest": manifest, "body": body}


def list_skills() -> dict:
    """All skill ids with their discovery descriptions."""
    from packages.skills.engage import load_index

    index = load_index()
    return {sid: facet.get("description", "") for sid, facet in sorted(index["skills"].items())}


def list_profiles() -> dict:
    """All profile ids with their domains/platforms."""
    import yaml

    out = {}
    for prof_path in sorted((ROOT / "profiles").glob("*.yaml")):
        try:
            data = yaml.safe_load(prof_path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        out[data.get("id", prof_path.stem)] = {
            "domains": data.get("domains", []),
            "platforms": data.get("platforms", []),
        }
    return out


def search_skills(query: str = "", domain: str | None = None,
                 standard: str | None = None) -> dict:
    """Ranked skill search over catalog.yaml (deterministic, stdlib only)."""
    import yaml

    cat_path = ROOT / "skills" / "catalog.yaml"
    if not cat_path.exists():
        return {"query": query, "results": []}
    cat = yaml.safe_load(cat_path.read_text(encoding="utf-8")) or {}
    q = query.lower()
    results = []
    for e in cat.get("skills", []):
        if domain and e.get("domain") != domain:
            continue
        if standard and standard not in (e.get("standards") or []):
            hay = " ".join([e.get("id", ""), e.get("title", ""),
                            str(e.get("standards", ""))]).lower()
            if standard.lower() not in hay:
                continue
        hay = " ".join([e.get("id", ""), e.get("title", ""),
                        " ".join(e.get("tags", []) or [])]).lower()
        score = sum(1 for tok in q.split() if tok and tok in hay)
        if not q or score:
            results.append({"id": e["id"], "title": e.get("title", ""),
                            "maturity": e.get("maturity", ""), "score": score})
    results.sort(key=lambda r: (-r["score"], r["id"]))
    return {"query": query, "count": len(results), "results": results}


def validate_skill(skill_id: str) -> dict:
    """Validate one skill's SKILL.md contract."""
    from packages.skills.loader import validate_skill_doc

    return validate_skill_doc(skill_id)


def run_skill(skill_id: str, repo_path: str = ".",
              target_files: list[str] | None = None, objective: str = "",
              constraints: str = "", output_dir: str | None = None,
              dry_run: bool = True) -> dict:
    """Execute a skill as a structured workflow (dry-run default)."""
    from packages.skills.runner import run_skill as _run

    return _run(skill_id, repo_path, target_files, objective, constraints,
                output_dir, dry_run)


def skill_report(skill_id: str, run_dir: str) -> dict:
    """Summarize a previous run_skill manifest directory."""
    import json

    mf = ROOT / run_dir / "run-manifest.json" if not str(run_dir).endswith(
        "run-manifest.json") else pathlib.Path(run_dir)
    data = json.loads(pathlib.Path(mf).read_text(encoding="utf-8"))
    return {"skill": skill_id, "manifest": data,
            "summary": f"{skill_id}: {len(data.get('generated_files', []))} "
                       f"file(s), checks={data.get('acceptance_checks', [])}"}
