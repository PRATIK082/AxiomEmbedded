"""Skill registry: load skills/catalog.yaml, index by id, detect duplicates/refs/cycles."""
from __future__ import annotations
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
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
                warnings.append(f"{sid}: unknown related_skill {rel}")
        for sub in e.get("sub_skills", []) or []:
            if sub not in ids:
                warnings.append(f"{sid}: unknown sub_skill {sub}")
        base = e.get("extends")
        if base and base not in ids:
            errors.append(f"{sid}: unknown extends base {base}")
        for ov in (e.get("domain_overlays", []) or []):
            if not (ROOT / "domains" / ov).is_dir():
                warnings.append(f"{sid}: missing domains overlay dir: {ov}")
        for ov in (e.get("platform_overlays", []) or []):
            if not (ROOT / "platforms" / ov).is_dir():
                warnings.append(f"{sid}: missing platforms overlay dir: {ov}")
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
