from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Iterable

@dataclass
class ArtifactGraph:
    edges: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))

    def add_edge(self, source: str, target: str, relationship: str = "related") -> None:
        self.edges[source].append((target, relationship))

    def neighbors(self, roots: Iterable[str], hops: int = 1) -> list[str]:
        seen: set[str] = set()
        queue = deque((r, 0) for r in roots)
        while queue:
            node, depth = queue.popleft()
            if node in seen:
                continue
            seen.add(node)
            if depth >= hops:
                continue
            for target, _ in self.edges.get(node, []):
                queue.append((target, depth + 1))
        return sorted(seen)
