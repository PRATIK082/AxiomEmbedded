"""Static analysis runner wrapper: cppcheck/clang-tidy invocation + SARIF-ish parse."""
from __future__ import annotations

import subprocess
from pathlib import Path

from packages.toolchain.detect import detect


def run_cppcheck(source_dir, extra=None, timeout=300):
    if not detect("cppcheck")["available"]:
        return {"status": "unavailable", "tool": "cppcheck",
                "install_hint": detect("cppcheck")["install_hint"]}
    src = Path(source_dir).resolve()
    cmd = ["cppcheck", "--enable=all", "--inline-suppr", str(src)] + (extra or [])
    res = subprocess.run(cmd, cwd=str(src), capture_output=True, text=True, timeout=timeout)
    out = (res.stderr or "") + (res.stdout or "")
    findings = []
    for line in out.splitlines():
        # cppcheck: [file:line]: (severity) message
        if ":" in line and "(" in line:
            findings.append(line.strip())
    return {"status": "ok" if res.returncode in (0,) else "findings",
            "returncode": res.returncode, "finding_count": len(findings),
            "findings_sample": findings[:50],
            "stdout_tail": (res.stdout or "")[-2000:],
            "stderr_tail": (res.stderr or "")[-2000:]}


def run_clang_tidy(source_dir, files=None, timeout=300):
    if not detect("clang-tidy")["available"]:
        return {"status": "unavailable", "tool": "clang-tidy",
                "install_hint": detect("clang-tidy")["install_hint"]}
    src = Path(source_dir).resolve()
    targets = files or []
    if not targets:
        targets = [str(p) for p in src.rglob("*.cpp")] + [str(p) for p in src.rglob("*.c")]
    cmd = ["clang-tidy"] + targets
    res = subprocess.run(cmd, cwd=str(src), capture_output=True, text=True, timeout=timeout)
    return {"status": "ok" if res.returncode == 0 else "findings",
            "returncode": res.returncode,
            "stdout_tail": (res.stdout or "")[-3000:],
            "stderr_tail": (res.stderr or "")[-2000:]}


def run_static(tool, source_dir, **kw):
    tool = (tool or "").lower()
    if tool in ("cppcheck",):
        return run_cppcheck(source_dir, kw.get("extra"))
    if tool in ("clang-tidy", "clangtidy"):
        return run_clang_tidy(source_dir, kw.get("files"))
    return {"status": "error", "message": f"unknown static tool: {tool}"}
