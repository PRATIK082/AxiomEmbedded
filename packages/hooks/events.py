"""Hook event types (ECC-aligned)."""
from __future__ import annotations

from enum import Enum


class HookEvent(str, Enum):
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"
    PRE_COMPACT = "PreCompact"
    STOP = "Stop"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"

    @classmethod
    def all(cls) -> list[str]:
        return [e.value for e in cls]


# Events where a failing hook aborts the action (fail-closed).
FAIL_CLOSED = {HookEvent.PRE_TOOL_USE.value}
# Events where hook failure is logged but does not block (fail-open).
FAIL_OPEN = {HookEvent.POST_TOOL_USE.value, HookEvent.SESSION_START.value,
             HookEvent.SESSION_END.value, HookEvent.PRE_COMPACT.value,
             HookEvent.STOP.value, HookEvent.USER_PROMPT_SUBMIT.value}
