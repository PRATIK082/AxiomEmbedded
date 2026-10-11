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
    # cycle detection over related_skills
    graph = {e["id"]: e.get("related_skills", []) or [] for e in data.get("skills", [])}
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
