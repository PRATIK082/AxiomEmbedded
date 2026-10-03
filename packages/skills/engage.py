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


def engage(domain: str | None = None, platform: str | None = None) -> dict:
    index = load_index()
    skills = {
        sid: facet
        for sid, facet in index["skills"].items()
        if _match(facet.get("domains", []), domain) and _match(facet.get("platforms", []), platform)
    }
    profiles = []
    for prof_path in sorted((ROOT / "profiles").glob("*.yaml")):
        try:
            data = yaml.safe_load(prof_path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if _match(data.get("domains", []), domain) and _match(data.get("platforms", []), platform):
            profiles.append(data.get("id", prof_path.stem))
    return {
        "domain": domain,
        "platform": platform,
        "skills": sorted(skills),
        "skill_count": len(skills),
        "profiles": sorted(profiles),
        "context_files": [f"skills/{s}/SKILL.md" for s in sorted(skills)],
    }
