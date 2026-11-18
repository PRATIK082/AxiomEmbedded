"""Domain/platform engagement: resolve which skills a project needs.

Matching rule: a skill engages when ("all" in its facets) or (the requested
value is listed). Profiles match when their domains/platforms intersect.
"""

from __future__ import annotations

import json
import pathlib

import yaml

from packages.paths import ROOT


def load_index() -> dict:
    p = ROOT / "registries" / "skill-index.json"
    if not p.exists():
        return {"skills": {}, "by_group": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"skills": {}, "by_group": {}}


def _match(facets: list[str], wanted: str | None) -> bool:
    if not wanted:
        return True
    return "all" in facets or wanted in facets


def engage(domain: str | None = None, platform: str | None = None,
           group: str | None = None, limit: int = 0,
           activity: str | None = None) -> dict:
    """Resolve which skills a project needs.

    group: restrict to a skills/groups.yaml view (unknown group -> error
    envelope). limit: cap returned skills for 1000+ skill trees (0 = all);
    capped replies carry total/truncated so callers can page (raise limit).
    activity: restrict to skills mapped to a DESA activity key (unknown or
    unindexed activity -> ok envelope with skill_count 0 and a warning so
    callers can surface the missing-context probe instead of silently
    proceeding).
    """
    index = load_index()
    # DESA activity facets come from the catalog (enriched by
    # scripts/enrich_catalog_facets.py); the JSON index carries only
    # domains/platforms. Skills with no mapped activity are excluded
    # when an activity filter is active.
    desa_activity: dict[str, str] = {}
    try:
        from packages.skills.registry import load_catalog
        _cat = load_catalog()
        enabled_ids = {e["id"] for e in _cat.get("skills", []) if e.get("enabled", True)}
        for e in _cat.get("skills", []):
            desa_activity[e["id"]] = (e.get("activity") or "")
    except Exception:
        enabled_ids = None
    if group is not None and group not in index.get("by_group", {}):
        known = sorted(index.get("by_group", {}))
        return {"status": "error", "domain": domain, "platform": platform,
                "group": group, "skills": [], "skill_count": 0, "total": 0,
                "truncated": False, "profiles": [], "context_files": [],
                "message": f"unknown skill group: {group} (known: {', '.join(known)})"}
    in_group = set(index.get("by_group", {}).get(group, [])) if group else None
    if activity:
        known_activities = sorted({a for a in desa_activity.values() if a})
        if activity not in known_activities:
            return {"status": "ok", "domain": domain, "platform": platform,
                    "group": group, "activity": activity,
                    "skills": [], "skill_count": 0, "total": 0,
                    "truncated": False, "profiles": [], "context_files": [],
                    "warning": f"no skills indexed for activity: {activity} "
                               f"(known: {', '.join(known_activities[:12])}"
                               f"{', ...' if len(known_activities) > 12 else ''})"}
    skills = {
        sid: facet
        for sid, facet in index["skills"].items()
        if (enabled_ids is None or sid in enabled_ids)
        and _match(facet.get("domains", []), domain) and _match(facet.get("platforms", []), platform)
        and (in_group is None or sid in in_group)
        and (not activity or desa_activity.get(sid, "") == activity)
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
        "activity": activity,
        "limit": limit,
        "skills": ordered,
        "skill_count": len(ordered),
        "total": total,
        "truncated": truncated,
        "profiles": sorted(profiles),
        "context_files": [f"skills/{s}/SKILL.md" for s in ordered],
    }
