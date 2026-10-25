"""Plugin API: discover and load third-party axiom plugins via entry points."""
from __future__ import annotations

import importlib.metadata
from pathlib import Path

ENTRY_GROUP = "axiom.plugins"


def list_plugins() -> list[dict]:
    out = []
    try:
        eps = importlib.metadata.entry_points()
        group = eps.select(group=ENTRY_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_GROUP, [])
    except Exception:
        group = []
    for ep in group:
        out.append({"name": ep.name, "value": ep.value})
    return out


def load_plugin(name: str):
    eps = importlib.metadata.entry_points()
    group = eps.select(group=ENTRY_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_GROUP, [])
    for ep in group:
        if ep.name == name:
            return ep.load()
    raise KeyError(f"plugin not found: {name}")
