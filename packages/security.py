"""Security helpers (Track E/F): secret scanning + redaction."""
from __future__ import annotations

import re
from pathlib import Path

SECRET_PATTERNS = [
    ("api-key", re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})")),
    ("token", re.compile(r"(?i)(token|secret|password|passwd)\s*[:=]\s*['\"]?([^\s'\"]{8,})")),
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github-pat", re.compile(r"ghp_[A-Za-z0-9]{30,}")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
]


def scan_text(text: str) -> list[dict]:
    findings = []
    for name, pat in SECRET_PATTERNS:
        for m in pat.finditer(text):
            findings.append({"type": name, "match": m.group(0)[:40], "offset": m.start()})
    return findings


def scan_path(path: str | Path) -> dict:
    p = Path(path)
    results = []
    files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        hits = scan_text(text)
        if hits:
            results.append({"file": str(f), "findings": hits})
    return {"scanned_files": len(files), "files_with_secrets": len(results),
            "results": results}


def redact(text: str) -> str:
    out = text
    for _name, pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out
