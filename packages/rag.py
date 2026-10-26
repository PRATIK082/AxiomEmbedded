"""Local document RAG (D11): keyword search over repo docs/skills/sources.

No external embeddings required; uses TF-IDF-ish scoring over tokenized text.
Optional sentence-transformers integration is documented but not required.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_CAMEL_RE = re.compile(r"[A-Z][a-z]+")


def _split_camel(tok: str) -> list[str]:
    return [m.group(0).lower() for m in _CAMEL_RE.finditer(tok)] or [tok.lower()]


def _tokens(text: str) -> list[str]:
    base = _TOKEN_RE.findall(text.lower())
    extra = []
    for m in re.finditer(r"[A-Za-z][a-z]+(?:[A-Z][a-z]+)+", text):
        extra.extend(_split_camel(m.group(0)))
    return base + extra


def build_index(roots: list[str | Path]) -> dict:
    docs = {}
    for root in roots:
        rp = Path(root)
        if rp.is_file():
            candidates = [rp]
        else:
            candidates = [p for p in rp.rglob("*") if p.is_file()
                          and p.suffix.lower() in (".md", ".txt", ".yaml", ".yml", ".py", ".c", ".h", ".rst")]
        for p in candidates:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            docs[str(p)] = _tokens(text)
    # document frequency
    df: dict[str, int] = {}
    for toks in docs.values():
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    n = len(docs) or 1
    idf = {t: math.log((n + 1) / (d + 1)) + 1 for t, d in df.items()}
    return {"docs": docs, "idf": idf, "n": n}


def search(index: dict, query: str, top_k: int = 5) -> list[dict]:
    qtoks = _tokens(query)
    if not qtoks:
        return []
    idf = index["idf"]
    results = []
    for path, toks in index["docs"].items():
        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        score = 0.0
        for qt in qtoks:
            if qt in tf:
                score += tf[qt] * idf.get(qt, 1.0)
        if score > 0:
            results.append({"path": path, "score": round(score, 3)})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


def search_with_snippet(index: dict, query: str, top_k: int = 5, snippet_chars: int = 200) -> list[dict]:
    """Like search but includes a text snippet from the matched doc."""
    from pathlib import Path
    hits = search(index, query, top_k)
    out = []
    for h in hits:
        snippet = ""
        try:
            text = Path(h["path"]).read_text(encoding="utf-8", errors="ignore")
            qlow = query.lower()
            idx = text.lower().find(qlow.split()[0] if qlow.split() else "")
            if idx >= 0:
                snippet = text[max(0, idx - 40): idx + snippet_chars]
        except OSError:
            pass
        out.append({**h, "snippet": snippet.strip()})
    return out
