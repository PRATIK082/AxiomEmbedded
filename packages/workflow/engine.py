from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class Workflow:
    id: str
    states: list[str]

def load(path: str | Path) -> Workflow:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Workflow(str(data.get("id", Path(path).stem)), [str(s.get("id", s)) if isinstance(s, dict) else str(s) for s in data.get("states", [])])
