"""Interactive confirmation helper for sensitive Axiom actions.

Wraps a callable: if policy disallows the action, prompts the operator
(yes/no) unless non-interactive, in which case it refuses.
"""
from __future__ import annotations

import sys
from typing import Callable, Any


SENSITIVE_ACTIONS = {"flash", "can-write", "ecu-write", "commit", "push", "merge",
                     "release", "production-write", "destructive"}


def confirm(action: str, detail: str = "", non_interactive: bool = False) -> bool:
    if action not in SENSITIVE_ACTIONS:
        return True
    if non_interactive or not sys.stdin.isatty():
        return False
    try:
        ans = input(f"Confirm sensitive action '{action}'? {detail} [y/N] ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def guard(action: str, fn: Callable[..., Any], *args, **kwargs) -> Any:
    if not confirm(action):
        return {"status": "denied", "action": action,
                "reason": "operator did not confirm (or non-interactive)"}
    return fn(*args, **kwargs)
