"""Domain/platform engagement: resolve which skills a project needs.

Matching rule: a skill engages when ("all" in its facets) or (the requested
value is listed). Profiles match when their domains/platforms intersect.
"""

from __future__ import annotations

import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_index() -> dict:
    return json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))


def _match(facets: list[str], wanted: str | None) -> bool:
    if not wanted:
        return True
    return "all" in facets or wanted in facets


def engage(domain: str | None = None, platform: str | None = None,
           group: str | None = None, limit: int = 0) -> dict:
    """Resolve which skills a project needs.

    group: restrict to a skills/groups.yaml view (unknown group -> error
    envelope). limit: cap returned skills for 1000+ skill trees (0 = all);
    capped replies carry total/truncated so callers can page (raise limit).
    """
    index = load_index()
    if group is not None and group not in index.get("by_group", {}):
        known = sorted(index.get("by_group", {}))
        return {"status": "error", "domain": domain, "platform": platform,
                "group": group, "skills": [], "skill_count": 0, "total": 0,
                "truncated": False, "profiles": [], "context_files": [],
                "message": f"unknown skill group: {group} (known: {', '.join(known)})"}
    in_group = set(index.get("by_group", {}).get(group, [])) if group else None
    skills = {
        sid: facet
        for sid, facet in index["skills"].items()
        if _match(facet.get("domains", []), domain) and _match(facet.get("platforms", []), platform)
        and (in_group is None or sid in in_group)
    }
    profiles = []
    for prof_path in sorted((ROOT / "profiles").glob("*.yaml")):
        try:
            data = yaml.safe_load(prof_path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if _match(data.get("domains", []), domain) and _match(data.get("platforms", []), platform):
            profiles.append(data.get("id", prof_path.stem))
    ordered = sorted(skills)
    total = len(ordered)
    truncated = bool(limit and total > limit)
    if limit:
        ordered = ordered[:limit]
    return {
        "status": "ok",
        "domain": domain,
        "platform": platform,
        "group": group,
        "limit": limit,
        "skills": ordered,
        "skill_count": len(ordered),
        "total": total,
        "truncated": truncated,
        "profiles": sorted(profiles),
        "context_files": [f"skills/{s}/SKILL.md" for s in ordered],
    }
