# SPDX-License-Identifier: Apache-2.0
"""Tool-candidate registry: the pluggable-tool surface behind `axiom packs`.

`registries/tool-candidates.yaml` records every open-source tool that can
plausibly be plugged into AxiomEmbedded, with its licence, install channel,
the extension point it serves, and the concrete benefit it brings.

This module is the read side of that registry. It never installs anything:
it resolves a candidate set for a domain/platform/standards request so an
agent (or a human) can decide what to adopt.

Matching rule mirrors `packages.skills.engage` and `packages.toolpacks.select`:
a candidate matches when ("all" in its facets) or the requested value is
listed. `status` filters to what is actually adoptable; `reference` and
`rejected` entries are recorded for auditability but never proposed.
"""

from __future__ import annotations

import pathlib
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registries" / "tool-candidates.yaml"

#: Statuses that may be proposed for adoption.
ADOPTABLE = ("candidate", "accepted")

#: Statuses kept for auditability but never proposed.
INFORMATIONAL = ("reference", "rejected")


def load_candidates() -> list[dict[str, Any]]:
    """All candidate records, in registry order."""
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    return list(data.get("candidates") or [])


def _match(facets: list[str], wanted: str | None) -> bool:
    if not wanted:
        return True
    return "all" in facets or wanted in facets


def select_candidates(
    domain: str | None = None,
    platform: str | None = None,
    standards: list[str] | None = None,
    category: str | None = None,
    status: str | None = None,
    include_informational: bool = False,
) -> dict[str, Any]:
    """Resolve the candidate tool set for a project request.

    Returns the matching candidates plus the derived install plan grouped by
    channel, so a caller can see at a glance which candidates are pure pip
    (trivially adoptable) and which need a container or a system package.
    """
    standards = standards or []
    allowed = set(ADOPTABLE)
    if include_informational:
        allowed |= set(INFORMATIONAL)
    if status:
        allowed = {status}

    matches: list[dict[str, Any]] = []
    for cand in load_candidates():
        if cand.get("status") not in allowed:
            continue
        if not _match(cand.get("domains") or [], domain):
            continue
        if not _match(cand.get("platforms") or [], platform):
            continue
        cand_standards = cand.get("standards") or []
        if standards and cand_standards and not any(s in cand_standards for s in standards):
            continue
        if category and category not in (cand.get("categories") or []):
            continue
        matches.append(cand)

    by_channel: dict[str, list[str]] = {}
    for cand in matches:
        by_channel.setdefault(cand.get("channel", "unknown"), []).append(cand["id"])

    by_milestone: dict[str, list[str]] = {}
    for cand in matches:
        by_milestone.setdefault(cand.get("milestone", "M0"), []).append(cand["id"])

    return {
        "domain": domain,
        "platform": platform,
        "standards": standards,
        "category": category,
        "candidate_count": len(matches),
        "candidates": [c["id"] for c in matches],
        "by_channel": {k: sorted(v) for k, v in sorted(by_channel.items())},
        "by_milestone": {k: sorted(v) for k, v in sorted(by_milestone.items())},
        "pip_install": sorted(
            c["install"] for c in matches
            if c.get("channel") == "pip" and c.get("install")
        ),
        "detail": matches,
    }
