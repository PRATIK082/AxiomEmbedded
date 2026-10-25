"""Requirements import: DOORS CSV / YAML / JSON -> artifact list.

Wraps parsing; never invents requirements. Returns a list of requirement
dicts suitable for writing to an assurance artifact (kind: safety-requirements
or a generic requirements list).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml


def import_csv(path: str | Path) -> list[dict]:
    out = []
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append({
                "id": (row.get("id") or row.get("ID") or row.get("ReqID") or "").strip(),
                "title": (row.get("title") or row.get("Title") or "").strip(),
                "text": (row.get("text") or row.get("description") or row.get("Description") or "").strip(),
                "priority": (row.get("priority") or row.get("Priority") or "").strip(),
                "source": str(path),
            })
    # assign ids if missing
    for i, r in enumerate(out, 1):
        if not r["id"]:
            r["id"] = f"REQ-{i}"
    return out


def import_yaml(path: str | Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    items = data.get("requirements") or data.get("items") or []
    out = []
    for i, r in enumerate(items, 1):
        if isinstance(r, str):
            r = {"text": r}
        out.append({
            "id": r.get("id") or f"REQ-{i}",
            "title": r.get("title", ""),
            "text": r.get("text") or r.get("description", ""),
            "priority": r.get("priority", ""),
            "source": str(path),
        })
    return out


def import_json(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data.get("requirements") or data if isinstance(data, list) else []
    out = []
    for i, r in enumerate(items, 1):
        if isinstance(r, str):
            r = {"text": r}
        out.append({
            "id": r.get("id") or f"REQ-{i}",
            "title": r.get("title", ""),
            "text": r.get("text") or r.get("description", ""),
            "priority": r.get("priority", ""),
            "source": str(path),
        })
    return out


def import_requirements(path: str | Path) -> list[dict]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return import_csv(p)
    if suffix in (".yaml", ".yml"):
        return import_yaml(p)
    if suffix == ".json":
        return import_json(p)
    raise ValueError(f"unsupported requirements format: {suffix}")


def write_requirements_artifact(reqs: list[dict], output: str | Path, domain: str = "generic-embedded") -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    doc = {
        "artifact_id": "REQ-IMPORTED",
        "schema_version": "1.0.0",
        "kind": "safety-requirements",
        "status": "draft",
        "domain": domain,
        "created_at": now,
        "updated_at": now,
        "author": "axiom",
        "approval_status": "draft",
        "requirements": reqs,
    }
    out.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return out
