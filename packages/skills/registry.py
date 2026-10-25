"""Skill registry: load skills/catalog.yaml, index by id, detect duplicates/refs/cycles."""
from __future__ import annotations
import pathlib
import yaml

from packages.paths import ROOT
CATALOG = ROOT / "skills" / "catalog.yaml"


def load_catalog(path: pathlib.Path | None = None) -> dict:
    p = pathlib.Path(path) if path else CATALOG
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data


def index_catalog(data: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for entry in data.get("skills", []):
        out[entry["id"]] = entry
    return out


def check_catalog(data: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    ids: set[str] = set(e["id"] for e in data.get("skills", []))
    required = {"id", "name", "version", "domain", "maturity", "path"}
    for e in data.get("skills", []):
        sid = e.get("id", "?")
        if sid in seen:
            errors.append(f"duplicate id: {sid}")
        seen.add(sid)
        missing = required - set(e.keys())
        if missing:
            errors.append(f"{sid}: missing fields {sorted(missing)}")
        for rel in e.get("related_skills", []) or []:
            if rel not in ids:
                errors.append(f"{sid}: unknown related_skill {rel}")
        for sub in e.get("sub_skills", []) or []:
            if sub not in ids:
                errors.append(f"{sid}: unknown sub_skill {sub}")
        base = e.get("extends")
        if base and base not in ids:
            errors.append(f"{sid}: unknown extends base {base}")
        for ov_kind, ov_key in (("domains", "domain_overlays"),
                                ("platforms", "platform_overlays")):
            for ov in (e.get(ov_key, []) or []):
                if not (ROOT / ov_kind / ov).is_dir():
                    warnings.append(f"{sid}: missing {ov_kind} overlay dir: {ov}")
    # related-symmetry: the graph is bidirectional by contract. A->B without
    # B->A is a drift error, not a style nit (agents navigate both ways).
    index = {e["id"]: e for e in data.get("skills", [])}
    for sid, e in index.items():
        for rel in e.get("related_skills", []) or []:
            if rel in index and sid not in (index[rel].get("related_skills", []) or []):
                errors.append(f"asymmetric related link: {sid} -> {rel} (missing back-link)")
    # cycle detection over extends only (related/sub are associative, not directed)
    graph = {e["id"]: ([e["extends"]] if e.get("extends") else [])
             for e in data.get("skills", [])}
    visited: dict[str, int] = {}

    def dfs(n: str, stack: list[str]):
        visited[n] = 1
        for m in graph.get(n, []):
            if m not in graph:
                continue
            if visited.get(m) == 1:
                errors.append(f"circular dependency: {' -> '.join(stack + [n, m])}")
            elif not visited.get(m):
                dfs(m, stack + [n])
        visited[n] = 2

    for n in graph:
        if not visited.get(n):
            dfs(n, [])
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "skill_count": len(ids)}


def resolve_extends(skill_id: str, index: dict[str, dict]) -> list[str]:
    """Base-skill chain for `extends` (nearest first). Guards against cycles."""
    chain: list[str] = []
    seen: set[str] = {skill_id}
    cur = (index.get(skill_id) or {}).get("extends")
    while cur and cur not in seen:
        chain.append(cur)
        seen.add(cur)
        cur = (index.get(cur) or {}).get("extends")
    return chain


LINK_KINDS = ("related_skills", "extends", "sub_skills",
              "domain_overlays", "platform_overlays")


def set_link(kind: str, skill_id: str, values: list[str],
             path: pathlib.Path | None = None) -> dict:
    """Edit the skill graph directly in catalog.yaml (single source).

    Replaces the old links.yaml workflow: no second file, no derivation
    step — edit, then run `axiom skills apply` to propagate + validate.
    `related_skills` edits auto-maintain the back-link (symmetry is a
    validation error, so this keeps the tree green in one call).
    """
    if kind not in LINK_KINDS:
        raise ValueError(f"unknown link kind {kind!r} (choose from {', '.join(LINK_KINDS)})")
    p = pathlib.Path(path) if path else CATALOG
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    idx = {e["id"]: e for e in data.get("skills", [])}
    if skill_id not in idx:
        raise ValueError(f"unknown skill: {skill_id}")
    for v in values:
        if kind in ("related_skills", "sub_skills", "extends") and v not in idx and v != skill_id:
            raise ValueError(f"unknown target skill: {v}")
    entry = idx[skill_id]
    if kind == "extends":
        if len(values) > 1:
            raise ValueError("extends takes at most one base skill")
        entry["extends"] = values[0] if values else None
    else:
        old = set(entry.get(kind, []) or [])
        entry[kind] = sorted(set(values))
        if kind == "related_skills":
            # auto-maintain back-links so symmetry validation stays green
            for other in old - set(values):
                if other in idx:
                    back = set(idx[other].get("related_skills", []) or [])
                    back.discard(skill_id)
                    idx[other]["related_skills"] = sorted(back)
            for other in set(values):
                if other in idx and other != skill_id:
                    back = set(idx[other].get("related_skills", []) or [])
                    back.add(skill_id)
                    idx[other]["related_skills"] = sorted(back)
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return {"skill": skill_id, "kind": kind, "values": entry.get(kind)}
