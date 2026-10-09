"""AxiomEmbedded Python SDK — single implementation behind every interface.

All other surfaces (MCP server, REST/A2A server, CLI additions) delegate to
these functions so SDK/CLI/MCP/REST/A2A always agree. Stdlib + PyYAML only.
"""

from __future__ import annotations

import pathlib

from packages.agents.router import route, detect_domain
from packages.skills.engage import engage

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
