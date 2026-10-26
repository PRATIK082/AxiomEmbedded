"""Hook runner: execute hook commands, collect results."""
from __future__ import annotations

import fnmatch
import json
import subprocess
import time
from pathlib import Path

from packages.hooks.events import FAIL_CLOSED, HookEvent
from packages.hooks.registry import hooks_for_event


def _match(hook: dict, tool_name: str | None) -> bool:
    matcher = hook.get("matcher")
    if not matcher or tool_name is None:
        return True
    return fnmatch.fnmatch(tool_name, matcher)


def run_hooks(event: str, payload: dict | None = None, tool_name: str | None = None,
              root: Path | None = None, timeout_default: int = 30) -> dict:
    """Run all hooks for ``event``. Returns {passed, results, blocked}.

    For fail-closed events, any non-zero hook blocks the action.
    """
    payload = payload or {}
    results = []
    blocked = False
    for h in hooks_for_event(event, root):
        if not _match(h, tool_name):
            continue
        cmd = h.get("command")
        script = h.get("script")
        if script:
            cmd = f"python {script}"
        if not cmd:
            continue
        timeout = int(h.get("timeout", timeout_default))
        start = time.time()
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                  timeout=timeout, cwd=str(root) if root else None,
                                  input=json.dumps(payload))
            rc = proc.returncode
            stdout = (proc.stdout or "").strip()
            stderr = (proc.stderr or "").strip()
        except subprocess.TimeoutExpired:
            rc = -1
            stdout = ""
            stderr = f"hook timed out after {timeout}s"
        except Exception as exc:  # noqa: BLE001
            rc = -1
            stdout = ""
            stderr = str(exc)
        passed = (rc == 0)
        results.append({"name": h.get("name", cmd), "event": event,
                        "returncode": rc, "passed": passed,
                        "stdout": stdout[:2000], "stderr": stderr[:2000],
                        "duration_s": round(time.time() - start, 3)})
        if not passed and event in FAIL_CLOSED:
            blocked = True
    overall_passed = all(r["passed"] for r in results) if results else True
    # fail-open events never block, even on failure
    if event not in FAIL_CLOSED:
        blocked = False
    return {"event": event, "passed": overall_passed, "blocked": blocked,
            "results": results, "hook_count": len(results)}
