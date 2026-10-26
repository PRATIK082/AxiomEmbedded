"""Hook system (Track E)."""
from packages.hooks.events import HookEvent, FAIL_CLOSED, FAIL_OPEN
from packages.hooks.registry import load_hooks, hooks_for_event
from packages.hooks.runner import run_hooks

__all__ = ["HookEvent", "FAIL_CLOSED", "FAIL_OPEN", "load_hooks",
           "hooks_for_event", "run_hooks"]
