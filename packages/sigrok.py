"""sigrok logic analyzer wrapper (D5)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _run(args: list[str]) -> dict:
    exe = shutil.which("sigrok-cli")
    if not exe:
        return {"status": "unavailable", "tool": "sigrok-cli",
                "install_hint": "install sigrok (sigrok.org)"}
    try:
        proc = subprocess.run([exe] + args, capture_output=True, text=True, timeout=120)
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    return {"status": "ok" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode, "stdout": proc.stdout,
            "stderr": proc.stderr}


def list_devices() -> dict:
    return _run(["--scan"])


def capture(channels: str, samples: int = 1000, output: str | None = None,
            driver: str | None = None) -> dict:
    args = ["-C", channels, "-n", str(samples)]
    if driver:
        args = ["-d", driver] + args
    if output:
        args += ["-o", output]
    return _run(args)


def decode(protocol: str, input_file: str) -> dict:
    return _run(["-i", input_file, "-P", protocol])
