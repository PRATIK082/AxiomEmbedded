from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass(frozen=True)
class ContextBudget:
    max_files: int = 24
    max_bytes: int = 500_000

class ContextSelector:
    """Backward-compatible graph selector plus index-backed context selection."""
    def __init__(self, graph=None, budget: ContextBudget | None = None):
        self.graph = graph
        self.budget = budget or ContextBudget()

    def select(self, roots):
        if self.graph is None:
            return list(roots)[: self.budget.max_files]
        selected = []
        queue = list(roots)
        while queue and len(selected) < self.budget.max_files:
            item = queue.pop(0)
            if item in selected:
                continue
            selected.append(item)
            try:
                queue.extend(self.graph.neighbors(item))
            except TypeError:
                queue.extend(self.graph.neighbors([item]))
        return selected

def select_from_index(index_path: str | Path, roots: list[str], budget: ContextBudget | None = None) -> list[str]:
    budget = budget or ContextBudget()
    data = json.loads(Path(index_path).read_text(encoding="utf-8"))
    files = data.get("files", [])
    selected: list[str] = []
    remaining = budget.max_bytes
    root_names = set(roots)
    candidates = sorted(files, key=lambda f: (0 if f.get("path") in root_names else 1, f.get("path", "")))
    for item in candidates:
        if len(selected) >= budget.max_files:
            break
        size = int(item.get("bytes", 0))
        if size > remaining:
            continue
        selected.append(item["path"])
        remaining -= size
    return selected
