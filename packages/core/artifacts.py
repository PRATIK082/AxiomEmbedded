from dataclasses import dataclass, field
from typing import Dict, List

@dataclass(frozen=True)
class Artifact:
    id: str
    kind: str
    version: str = "0.1.0"
    status: str = "draft"
    metadata: Dict[str, str] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
