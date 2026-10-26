"""Hook registry: load hooks from .axiom/hooks.yaml or hooks/ directories."""
from __future__ import annotations

import pathlib
import yaml

from packages.paths import ROOT


def _candidate_paths(root: pathlib.Path | None = None) -> list[pathlib.Path]:
    r = root or ROOT
    out = []
    for p in (r / ".axiom" / "hooks.yaml", r / ".axiom" / "hooks.yml",
              r / "hooks" / "hooks.yaml", r / "hooks" / "hooks.yml"):
        if p.exists():
            out.append(p)
    return out


def load_hooks(root: pathlib.Path | None = None) -> dict[str, list[dict]]:
    """Return {event: [hook_spec, ...]}.

    Hook spec schema:
      - name: str
      - event: str (HookEvent value)
      - command: str (shell command) OR script: str (path to script)
      - matcher: str (optional tool-name glob for Pre/PostToolUse)
      - timeout: int seconds (default 30)
      - enabled: bool (default True)
    """
    hooks: dict[str, list[dict]] = {}
    for p in _candidate_paths(root):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for h in (data.get("hooks") or []):
            if not isinstance(h, dict):
                continue
            event = h.get("event")
            if not event:
                continue
            hooks.setdefault(event, []).append(h)
    return hooks


def hooks_for_event(event: str, root: pathlib.Path | None = None) -> list[dict]:
    return [h for h in load_hooks(root).get(event, []) if h.get("enabled", True)]
