# SPDX-License-Identifier: Apache-2.0
"""Rule-based skill groups: named views over the catalog (no dir moves).

groups.yaml semantics: `match_any` is OR; each clause is AND across keys,
OR within a key's list. Keys: id, id_prefix, domain, subdomain, tags,
maturity. All matching reads catalog.yaml entries (single source).
"""

from __future__ import annotations

import pathlib

import yaml

from packages.paths import ROOT
GROUPS_PATH = ROOT / "skills" / "groups.yaml"


def load_groups(path: pathlib.Path | None = None) -> dict:
    return yaml.safe_load((path or GROUPS_PATH).read_text(encoding="utf-8")) or {}


def _clause_matches(entry: dict, clause: dict) -> bool:
    for key, want in clause.items():
        want_list = want if isinstance(want, list) else [want]
        if key == "id":
            if entry.get("id") not in want_list:
                return False
        elif key == "id_prefix":
            if not any(str(entry.get("id", "")).startswith(p) for p in want_list):
                return False
        elif key in ("domain", "subdomain", "maturity"):
            if entry.get(key) not in want_list:
                return False
        elif key == "tags":
            if not (set(entry.get("tags", [])) & set(want_list)):
                return False
        else:
            raise ValueError(f"unknown group match key: {key}")
    return True


def group_members(catalog: dict, groups: dict | None = None) -> dict[str, list[str]]:
    """Evaluate groups.yaml over catalog entries -> {group: sorted skill ids}."""
    groups = groups if groups is not None else load_groups()
    out: dict[str, list[str]] = {}
    for gname, gdef in (groups.get("groups", {}) or {}).items():
        clauses = gdef.get("match_any", [])
        members = [e["id"] for e in catalog.get("skills", [])
                   if e.get("enabled", True) and any(_clause_matches(e, c) for c in clauses)]
        out[gname] = sorted(members)
    return out


def validate_groups(catalog: dict, groups: dict | None = None) -> list[str]:
    """Invariant: every enabled skill matches >= 1 group. Returns errors."""
    members = group_members(catalog, groups)
    covered = {sid for ids in members.values() for sid in ids}
    return [f"skill {e['id']} matches no group"
            for e in catalog.get("skills", [])
            if e.get("enabled", True) and e["id"] not in covered]
