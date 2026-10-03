from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass(frozen=True)
class RegistryEntry:
    id: str
    path: str

def load_registry(path: str | Path) -> list[RegistryEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data.get("agents") or data.get("skills") or data.get("domains") or data.get("platforms") or []
    return [RegistryEntry(str(item["id"] if isinstance(item, dict) else item), str(item.get("path", "")) if isinstance(item, dict) else "") for item in items]
