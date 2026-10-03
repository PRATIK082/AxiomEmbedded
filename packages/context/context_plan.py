from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ContextPlan:
    roots: list[str]
    reasons: list[str]
    max_files: int
    max_tokens: int


def plan_for_change(roots: list[str], max_files: int = 24, max_tokens: int = 12000) -> ContextPlan:
    reasons = [f"explicit root: {r}" for r in roots]
    return ContextPlan(roots=roots, reasons=reasons, max_files=max_files, max_tokens=max_tokens)
