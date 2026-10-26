"""Test runner wrapper: invoke unit/system test frameworks and parse results.

Wraps best-in-class OSS runners (ceedling, pytest, gtest). Never reimplements.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

from packages.toolchain.detect import detect


def _run(cmd, cwd, timeout=600):
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        return {"status": "unavailable", "returncode": 127, "stdout": "", "stderr": str(exc),
                "passed": 0, "failed": 0, "duration_s": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "returncode": -1, "stdout": "", "stderr": "timeout",
                "passed": 0, "failed": 0, "duration_s": round(time.time() - start, 2)}
    return {"status": "ok" if rc == 0 else "failed", "returncode": rc,
            "stdout_tail": (out or "")[-3000:], "stderr_tail": (err or "")[-2000:],
            "duration_s": round(time.time() - start, 2), "_out": out or "", "_err": err or ""}


def run_pytest(source_dir, args=None, timeout=600):
    src = Path(source_dir).resolve()
    cmd = ["python", "-m", "pytest", "-q"] + (args or [])
    res = _run(cmd, src, timeout)
    out = res.pop("_out", "")
    err = res.pop("_err", "")
    m = re.search(r"(\d+) passed", out + err)
    passed = int(m.group(1)) if m else 0
    m = re.search(r"(\d+) failed", out + err)
    failed = int(m.group(1)) if m else 0
    res["passed"] = passed
    res["failed"] = failed
    res["framework"] = "pytest"
    return res


def run_ceedling(source_dir, task="test:all", timeout=600):
    if not detect("ceedling")["available"]:
        return {"status": "unavailable", "tool": "ceedling",
                "install_hint": detect("ceedling")["install_hint"]}
    src = Path(source_dir).resolve()
    res = _run(["ceedling", task], src, timeout)
    out = res.pop("_out", "")
    err = res.pop("_err", "")
    m = re.search(r"(\d+)\s+Tests\s+(\d+)\s+Failures", out + err, re.I)
    passed = int(m.group(1)) - int(m.group(2)) if m else 0
    failed = int(m.group(2)) if m else 0
    res["passed"] = passed
    res["failed"] = failed
    res["framework"] = "ceedling"
    return res


def run_tests(framework: str, source_dir: str | Path, **kw) -> dict:
    fw = (framework or "").lower()
    if fw in ("pytest", "python"):
        return run_pytest(source_dir, kw.get("args"))
    if fw in ("ceedling", "unity"):
        return run_ceedling(source_dir, kw.get("task", "test:all"))
    return {"status": "error", "message": f"unknown test framework: {framework}"}
