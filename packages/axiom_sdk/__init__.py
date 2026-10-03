"""AxiomEmbedded Python SDK.

Client-neutral entry point: same engage/plan/read operations back the CLI,
MCP server, REST server, and direct Python use — one implementation, every
interface. No third-party dependencies beyond what the platform already uses.

Quick start::

    from packages.axiom_sdk import engage, run_plan, read_skill

    sel = engage(domain="automotive", platform="mcu")
    plan = run_plan("Add watchdog supervision to the motor driver")
    body = read_skill("mcu")
"""

from __future__ import annotations

import pathlib

from packages.agents.router import route
from packages.skills.engage import engage as engage
from packages.skills.engage import load_index
from packages.axiom_ops import get_status as get_status
from packages.axiom_ops import plan_fix as plan_fix
from packages.axiom_ops import plan_feature as plan_feature

ROOT = pathlib.Path(__file__).resolve().parents[2]

APPROVAL_REQUIRED_FOR = [
    "git push",
    "release",
    "destructive_command",
    "safety_critical_change",
    "security_critical_change",
]

__all__ = [
    "engage",
    "run_plan",
    "read_skill",
    "list_skills",
    "list_profiles",
    "get_status",
    "plan_fix",
    "plan_feature",
    "APPROVAL_REQUIRED_FOR",
]


def run_plan(request: str, domain: str | None = None, platform: str | None = None) -> dict:
    """Opencode-style plan-then-execute plan. The host harness provides the model."""
    selection = engage(domain, platform)
    return {
        "mode": "plan-then-execute",
        "request": request,
        "intent": route(request),
        "engagement": selection,
        "phases": ["plan", "implement", "verify", "evidence"],
        "context_files": selection["context_files"],
        "approval_required_for": list(APPROVAL_REQUIRED_FOR),
    }


def read_skill(skill_id: str) -> str:
    """Full SKILL.md body (including frontmatter) for one skill. Raises KeyError."""
    path = ROOT / "skills" / skill_id / "SKILL.md"
    if not path.exists():
        raise KeyError(f"unknown skill: {skill_id}")
    return path.read_text(encoding="utf-8")


def list_skills() -> list[str]:
    return sorted(load_index()["skills"])


def list_profiles() -> list[str]:
    import yaml

    profiles = []
    for prof_path in sorted((ROOT / "profiles").glob("*.yaml")):
        try:
            data = yaml.safe_load(prof_path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        profiles.append(data.get("id", prof_path.stem))
    return profiles
