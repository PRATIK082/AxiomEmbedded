"""Coverage ingestion wrapper: run gcovr/lcov and parse thresholds."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from packages.toolchain.detect import detect


def run_gcovr(source_dir, output_format="text", threshold=None, timeout=300):
    if not detect("gcovr")["available"]:
        return {"status": "unavailable", "tool": "gcovr",
                "install_hint": detect("gcovr")["install_hint"]}
    src = Path(source_dir).resolve()
    cmd = ["gcovr", "--root", str(src)]
    if output_format == "json":
        cmd += ["--json"]
    res = subprocess.run(cmd, cwd=str(src), capture_output=True, text=True, timeout=timeout)
    out = res.stdout or ""
    coverage = None
    if output_format == "json":
        try:
            data = json.loads(out)
            coverage = data.get("line_coverage") or data.get("percent_covered")
        except Exception:
            pass
    if coverage is None:
        m = re.search(r"TOTAL.*?(\d+(?:\.\d+)?)%", out)
        if m:
            coverage = float(m.group(1))
    status = "ok" if res.returncode == 0 else "failed"
    if threshold is not None and coverage is not None and coverage < threshold:
        status = "below_threshold"
    return {"status": status, "returncode": res.returncode,
            "coverage_percent": coverage, "threshold": threshold,
            "stdout_tail": out[-3000:], "stderr_tail": (res.stderr or "")[-1000:]}


def run_coverage(tool, source_dir, **kw):
    tool = (tool or "").lower()
    if tool in ("gcovr", "gcov"):
        return run_gcovr(source_dir, kw.get("format", "text"), kw.get("threshold"))
    return {"status": "error", "message": f"unknown coverage tool: {tool}"}
