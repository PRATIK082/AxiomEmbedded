"""Token budgeting helpers for Axiom context selection.

Uses tiktoken when available (optional dep) and falls back to a
char/4 heuristic so the core never hard-depends on a tokenizer.
"""
from __future__ import annotations

import pathlib

try:
    import tiktoken  # type: ignore

    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - env dependent
    _ENC = None


def count_tokens(text: str) -> int:
    if not text:
        return 0
    if _ENC is not None:
        try:
            return len(_ENC.encode(text))
        except Exception:
            pass
    # heuristic: ~4 chars per token for English-ish text
    return max(1, len(text) // 4)


def count_file_tokens(path: str | pathlib.Path) -> int:
    try:
        return count_tokens(pathlib.Path(path).read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return 0


class TokenBudget:
    """Track consumed tokens against a cap; exposes remaining headroom."""

    def __init__(self, cap: int = 8000):
        self.cap = cap
        self.used = 0

    def remaining(self) -> int:
        return max(0, self.cap - self.used)

    def can_fit(self, n: int) -> bool:
        return self.used + n <= self.cap

    def consume(self, n: int) -> bool:
        if not self.can_fit(n):
            return False
        self.used += n
        return True

    def reset(self) -> None:
        self.used = 0
