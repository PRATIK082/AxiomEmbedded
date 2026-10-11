"""Domain/platform engagement: resolve which skills a project needs.

Matching rule: a skill engages when ("all" in its facets) or (the requested
value is listed). Profiles match when their domains/platforms intersect.
"""

from __future__ import annotations

import json
import os
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _is_content_root(p: pathlib.Path) -> bool:
    # NOTE: must include the registries marker file. Checking only
    # skills/+agents/ dirs false-matches an installed wheel, which ships
    # the *Python packages* packages/skills/ and packages/agents/.
    return ((p / "skills").is_dir() and (p / "agents").is_dir()
            and (p / "registries" / "skills.json").is_file())


def content_root() -> pathlib.Path | None:
    """Locate the Axiom content tree (skills/, registries/, agents/).

    Source checkout: found by walking up from this file. Installed wheel
    (site-packages has no content tree): honors $AXIOM_CONTENT, else None
    so callers degrade gracefully instead of raising FileNotFoundError.
    """
    env = os.environ.get("AXIOM_CONTENT")
    if env:
        cand = pathlib.Path(env)
        if _is_content_root(cand):
            return cand
    here = pathlib.Path(__file__).resolve()
    for parent in [here.parents[2]] + list(here.parents):
        if _is_content_root(parent):
            return parent
    return None


def load_index() -> dict | None:
    root = content_root()
    if root is None:
        return None
    try:
        return json.loads((root / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _match(facets: list[str], wanted: str | None) -> bool:
    if not wanted:
        return True
    return "all" in facets or wanted in facets


def engage(domain: str | None = None, platform: str | None = None) -> dict:
    root = content_root()
    index = load_index()
    if root is None or index is None:
        return {
            "domain": domain,
            "platform": platform,
            "skills": [],
            "skill_count": 0,
            "profiles": [],
            "context_files": [],
            "note": ("no Axiom content tree found (pip-installed CLI without content). "
                     "Run from a source checkout or set AXIOM_CONTENT to the repo dir."),
        }
    skills = {
        sid: facet
        for sid, facet in index["skills"].items()
        if _match(facet.get("domains", []), domain) and _match(facet.get("platforms", []), platform)
    }
    profiles = []
    for prof_path in sorted((root / "profiles").glob("*.yaml")):
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
