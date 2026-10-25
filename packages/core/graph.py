from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Dict, Iterable, Set, Tuple

@dataclass
class ArtifactGraph:
    """Typed artifact graph.

    Nodes carry metadata; edges are relationship-typed (source -> (target, rel)).
    Backward-compatible with the old simple graph API: ``link``/``add_node``/
    ``neighbors(node_id)`` keep working, while ``add_edge``/``reach`` expose
    the richer multi-hop traversal.
    """
    nodes: Dict[str, dict] = field(default_factory=dict)
    edges: Dict[str, list[Tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))

    def add_node(self, node_id: str, data: dict | None = None) -> None:
        self.nodes[node_id] = data or {}
        self.edges.setdefault(node_id, [])

    def link(self, source: str, target: str) -> None:
        self.add_edge(source, target, "related")

    def add_edge(self, source: str, target: str, relationship: str = "related") -> None:
        self.nodes.setdefault(source, {})
        self.nodes.setdefault(target, {})
        self.edges.setdefault(source, []).append((target, relationship))

    def neighbors(self, node_id) -> list[str]:
        """Direct (1-hop) neighbour ids for a single node."""
        out: list[str] = []
        for target, _ in self.edges.get(node_id if isinstance(node_id, str) else str(node_id), []):
            out.append(target)
        # de-dup preserving order
        seen: set[str] = set()
        result: list[str] = []
        for t in out:
            if t not in seen:
                seen.add(t)
                result.append(t)
        return sorted(result)

    def reach(self, roots: Iterable[str], hops: int = 1) -> list[str]:
        """BFS up to ``hops`` from ``roots``; returns sorted unique node ids
        (including roots), matching the old artifact_graph semantics."""
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

    def neighbors_with_rel(self, node_id: str) -> list[Tuple[str, str]]:
        return list(self.edges.get(node_id, []))
