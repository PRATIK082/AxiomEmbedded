"""AxiomEmbedded ops layer: Simple UI, Complex Automation (slice 1).

One implementation behind the terminal dashboard (`axiom status`), the
`/` HTML dashboard on `axiom serve`, and the `axiom fix` / `axiom feature`
plan emitters. All metrics are real repository data — no fixtures.

Design rule from the feature spec: the user sees status and next action;
YAML paths, branch names, and matrix structures stay hidden unless
`--format json` (Level 4: raw data) is requested.
"""

from __future__ import annotations

import json
import pathlib
from collections import Counter

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Fix-defect workflow: 10 internal steps from the feature spec §3 (INTENT ..
# PR). The harness executes; axiom emits the plan with context attached.
FIX_STEPS = [
    "intent",
    "context",
    "impact",
    "root_cause",
    "patch",
    "tests",
    "analysis",
    "review",
    "evidence",
    "pr",
]

# Add-feature workflow: 9 internal steps from the feature spec §3.
FEATURE_STEPS = [
    "intent",
    "context",
    "design",
    "implement",
    "tests",
    "traceability",
    "compliance",
    "evidence",
    "pr",
]

APPROVAL_REQUIRED_FOR = [
    "git push",
    "release",
    "destructive_command",
    "safety_critical_change",
    "security_critical_change",
]


def _read_yaml(path: pathlib.Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _skill_health() -> dict:
    registry = json.loads((ROOT / "registries" / "skills.json").read_text(encoding="utf-8"))
    ids = [s["id"] for s in registry.get("skills", [])]
    versions: dict[str, str] = {}
    missing_manifest: list[str] = []
    for sid in ids:
        manifest = ROOT / "skills" / sid / "manifest.yaml"
        if manifest.exists():
            versions[sid] = str(_read_yaml(manifest).get("version", "unknown"))
        else:
            missing_manifest.append(sid)
    counts = Counter(versions.values())
    latest = max(counts) if counts else "unknown"
    stale = sorted(s for s, v in versions.items() if v != latest)
    return {
        "total": len(ids),
        "versions": dict(counts),
        "latest": latest,
        "stale": stale,
        "missing_manifest": missing_manifest,
    }


def _inventory() -> dict:
    def count(pattern: str) -> int:
        return len(list(ROOT.glob(pattern)))

    return {
        "schemas": count("schemas/*.schema.json"),
        "profiles": count("profiles/*.yaml"),
        "workflows": count("workflows/*.yaml"),
        "agents": sum(1 for p in (ROOT / "agents").iterdir() if p.is_dir()),
        "domains": sum(1 for p in (ROOT / "domains").iterdir() if p.is_dir()) if (ROOT / "domains").exists() else 0,
        "tests": count("tests/test_*.py"),
    }


def get_status() -> dict:
    """Project health of this repository: skills, inventory, attention items."""
    skills = _skill_health()
    attention: list[dict] = []
    for sid in skills["stale"]:
        attention.append(
            {
                "severity": "medium",
                "id": f"STALE-{sid}",
                "title": f"Skill '{sid}' is behind the latest version ({skills['latest']})",
                "action": f"axiom run 'deep-update {sid}'",
            }
        )
    for sid in skills["missing_manifest"]:
        attention.append(
            {
                "severity": "high",
                "id": f"MISSING-{sid}",
                "title": f"Skill '{sid}' has no manifest.yaml",
                "action": f"axiom run 'restore manifest for {sid}'",
            }
        )
    state = "healthy" if not attention else "needs_attention"
    recommended = attention[0]["action"] if attention else "axiom run 'next feature'"
    return {
        "project": "AxiomEmbedded",
        "state": state,
        "skills": skills,
        "inventory": _inventory(),
        "needs_attention": attention,
        "recommended_next_action": recommended,
    }


def plan_fix(issue_id: str, domain: str | None = None, platform: str | None = None) -> dict:
    """Emit the 10-step fix-defect plan for a harness agent to execute."""
    from packages.skills.engage import engage

    selection = engage(domain, platform)
    return {
        "mode": "plan-then-execute",
        "kind": "fix",
        "issue_id": issue_id,
        "steps": list(FIX_STEPS),
        "engagement": selection,
        "context_files": selection["context_files"],
        "evidence_target": "docs/compliance/evidence/",
        "approval_required_for": list(APPROVAL_REQUIRED_FOR),
    }


def plan_feature(feature_id: str, domain: str | None = None, platform: str | None = None) -> dict:
    """Emit the 9-step add-feature plan for a harness agent to execute."""
    from packages.skills.engage import engage

    selection = engage(domain, platform)
    return {
        "mode": "plan-then-execute",
        "kind": "feature",
        "feature_id": feature_id,
        "steps": list(FEATURE_STEPS),
        "engagement": selection,
        "context_files": selection["context_files"],
        "evidence_target": "docs/compliance/evidence/",
        "approval_required_for": list(APPROVAL_REQUIRED_FOR),
    }
