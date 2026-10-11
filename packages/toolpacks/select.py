"""Plug-and-play toolpack selection: resolve which tools/pip packs a project needs.

Matching rule mirrors skills engage: a tool engages when ("all" in its facets)
or (the requested value is listed). Standards: tools with an empty standards
facet are generic and always match; otherwise at least one requested standard
must be listed. Agents engage when their manifest `skills` intersect the
engaged skills, so external CLI agents only surface where their skills apply.
"""

from __future__ import annotations

import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_tool_index() -> dict:
    return json.loads((ROOT / "registries" / "tool-index.json").read_text(encoding="utf-8"))


def _match(facets: list[str], wanted: str | None) -> bool:
    if not wanted:
        return True
    return "all" in facets or wanted in facets


def _match_standards(tool_standards: list[str], wanted: list[str]) -> bool:
    if not wanted:
        return True
    if not tool_standards:
        return True  # generic tooling applies regardless of standard
    return any(s in tool_standards for s in wanted)


def select_packs(
    domain: str | None = None,
    platform: str | None = None,
    standards: list[str] | None = None,
) -> dict:
    standards = standards or []
    index = load_tool_index()
    tools = {
        tid: facet
        for tid, facet in index["tools"].items()
        if _match(facet.get("domains", []), domain)
        and _match(facet.get("platforms", []), platform)
        and _match_standards(facet.get("standards", []), standards)
    }
    install = []
    for tid in sorted(tools):
        try:
            manifest = yaml.safe_load(
                (ROOT / "tools" / tid / "manifest.yaml").read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        deps = manifest.get("dependencies", [])
        if deps:
            install.append({"tool": tid, "pip": deps})

    from packages.skills.engage import engage

    skills = set(engage(domain, platform)["skills"])
    agents = []
    try:
        registry = json.loads((ROOT / "registries" / "agents.json").read_text(encoding="utf-8"))
        for entry in registry.get("agents", []):
            try:
                manifest = json.loads((ROOT / entry["manifest"]).read_text(encoding="utf-8"))
            except Exception:
                continue
            wanted_skills = set(manifest.get("skills", []))
            if wanted_skills and wanted_skills & skills:
                agents.append(entry["id"])
    except Exception:
        pass
    return {
        "domain": domain,
        "platform": platform,
        "standards": standards,
        "tools": sorted(tools),
        "tool_count": len(tools),
        "install": install,
        "agents": sorted(agents),
        "skills": sorted(skills),
        "manifests": [f"tools/{t}/manifest.yaml" for t in sorted(tools)],
    }
