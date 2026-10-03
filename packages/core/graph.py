from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class ArtifactGraph:
    nodes: Dict[str, dict] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)

    def add_node(self, node_id: str, data: dict):
        self.nodes[node_id] = data
        self.edges.setdefault(node_id, set())

    def link(self, source: str, target: str):
        self.edges.setdefault(source, set()).add(target)

    def neighbors(self, node_id: str):
        return sorted(self.edges.get(node_id, set()))
