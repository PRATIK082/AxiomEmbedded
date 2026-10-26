"""Strategic context compaction (B6).

Compacts a list of messages/turns into a summary when token usage crosses a
threshold (default 50% of cap), preserving the most recent turns and a
system prompt. Deterministic; no model calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from packages.context.tokens import count_tokens


@dataclass
class Turn:
    role: str  # system | user | assistant | tool
    content: str
    tokens: int = 0

    def __post_init__(self):
        if self.tokens == 0:
            self.tokens = count_tokens(self.content)


@dataclass
class CompactionPlan:
    keep: list[Turn] = field(default_factory=list)
    compacted: list[Turn] = field(default_factory=list)
    summary: str = ""
    before_tokens: int = 0
    after_tokens: int = 0
    triggered: bool = False


def should_compact(turns: list[Turn], cap: int, threshold: float = 0.5) -> bool:
    total = sum(t.tokens for t in turns)
    return total > int(cap * threshold)


def compact(turns: list[Turn], cap: int = 8000, threshold: float = 0.5,
            keep_recent: int = 4) -> CompactionPlan:
    """Compact older turns into a summary; keep the last ``keep_recent`` turns.

    System turns are always retained. Returns a plan describing what was kept
    and what was folded into the summary.
    """
    plan = CompactionPlan()
    plan.before_tokens = sum(t.tokens for t in turns)
    if not should_compact(turns, cap, threshold):
        plan.keep = list(turns)
        plan.after_tokens = plan.before_tokens
        plan.triggered = False
        return plan
    plan.triggered = True
    system_turns = [t for t in turns if t.role == "system"]
    others = [t for t in turns if t.role != "system"]
    to_compact = others[:-keep_recent] if keep_recent > 0 else list(others)
    to_keep_recent = others[-keep_recent:] if keep_recent > 0 else []
    # Build a deterministic summary of compacted turns.
    lines = []
    for t in to_compact:
        snippet = t.content.strip().replace("\n", " ")[:120]
        lines.append(f"- [{t.role}] {snippet}")
    plan.summary = "Compacted turns:\n" + "\n".join(lines)
    plan.compacted = to_compact
    plan.keep = system_turns + [Turn(role="assistant", content=plan.summary,
                                     tokens=count_tokens(plan.summary))] + to_keep_recent
    plan.after_tokens = sum(t.tokens for t in plan.keep)
    return plan
