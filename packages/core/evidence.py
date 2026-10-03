from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib, json
from pathlib import Path

@dataclass
class EvidenceRecord:
    id: str
    action: str
    source_baseline: str
    agent: str = "unknown"
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    verification: dict = field(default_factory=dict)
    approval: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

def append_evidence(path: str | Path, record: EvidenceRecord) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**asdict(record), "digest": record.digest}, sort_keys=True) + "\n")
