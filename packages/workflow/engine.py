from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass(frozen=True)
class Workflow:
    id: str
    version: str = "1.0.0"
    states: list[str] = field(default_factory=list)
    gates: list[str] = field(default_factory=list)

def load(path: str | Path) -> Workflow:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    states = [str(s.get("id", s)) if isinstance(s, dict) else str(s) for s in data.get("states", [])]
    gates = [str(g) for g in (data.get("gates", []) or [])]
    return Workflow(str(data.get("id", Path(path).stem)), str(data.get("version", "1.0.0")), states, gates)
