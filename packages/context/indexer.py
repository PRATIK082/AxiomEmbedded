from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, json, re

@dataclass(frozen=True)
class FileRecord:
    path: str
    bytes: int
    sha256: str
    language: str
    includes: list[str]

def language_for(path: Path) -> str:
    return {".c":"c",".h":"c",".cc":"cpp",".cpp":"cpp",".hpp":"cpp",".rs":"rust",".py":"python",".yaml":"yaml",".yml":"yaml",".json":"json",".md":"markdown"}.get(path.suffix.lower(), "other")

def scan(root: str | Path) -> list[FileRecord]:
    root = Path(root)
    out: list[FileRecord] = []
    ignored = {".git", ".pytest_cache", "__pycache__", ".venv", "build", "dist"}
    for p in root.rglob("*"):
        if not p.is_file() or any(part in ignored for part in p.parts):
            continue
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        text = raw[:1_000_000].decode("utf-8", errors="ignore") if len(raw) <= 1_000_000 else ""
        includes = re.findall(r'^\s*#include\s*[<\"]([^>\"]+)[>\"]', text, flags=re.MULTILINE) if language_for(p) in {"c","cpp"} else []
        out.append(FileRecord(str(p.relative_to(root)), len(raw), hashlib.sha256(raw).hexdigest(), language_for(p), includes))
    return sorted(out, key=lambda x: x.path)

def write_index(root: str | Path, output: str | Path) -> int:
    records = [asdict(r) for r in scan(root)]
    payload = {"schema_version":"1.0","root":str(Path(root).resolve()),"files":records}
    p = Path(output); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return len(records)
