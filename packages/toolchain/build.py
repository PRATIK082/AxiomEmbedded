"""Build toolchain wrapper: detect + invoke + parse errors.

Wraps best-in-class OSS build systems (cmake/make/ninja/west/pio). Never
reimplements a compiler. Returns structured results with parsed diagnostics.
"""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from packages.toolchain.detect import detect

# gcc/clang-style diagnostic: file:line:col: severity: message
DIAG_RE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+):\s*(?P<sev>error|warning|note):\s*(?P<msg>.*)$")


def parse_diagnostics(text: str) -> list[dict]:
    out = []
    for line in (text or "").splitlines():
        m = DIAG_RE.match(line.strip())
        if m:
            out.append({"file": m.group("file"), "line": int(m.group("line")),
                        "column": int(m.group("col")), "severity": m.group("sev"),
                        "message": m.group("msg")})
    return out


def _run(cmd: list[str], cwd: Path, timeout: int = 600) -> dict:
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                              timeout=timeout)
        rc = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        return {"status": "error", "returncode": 127, "command": cmd,
                "stdout": "", "stderr": str(exc), "diagnostics": [],
                "duration_s": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "returncode": -1, "command": cmd,
                "stdout": "", "stderr": f"timed out after {timeout}s",
                "diagnostics": [], "duration_s": round(time.time() - start, 2)}
    combined = (stdout or "") + "\n" + (stderr or "")
    diags = parse_diagnostics(combined)
    errors = [d for d in diags if d["severity"] == "error"]
    warnings = [d for d in diags if d["severity"] == "warning"]
    return {
        "status": "ok" if rc == 0 else "failed",
        "returncode": rc,
        "command": cmd,
        "stdout_tail": (stdout or "")[-2000:],
        "stderr_tail": (stderr or "")[-2000:],
        "diagnostics": diags,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "duration_s": round(time.time() - start, 2),
    }


def cmake_configure(source_dir: str | Path, build_dir: str | Path,
                    generator: str | None = None, extra: list[str] | None = None) -> dict:
    if not detect("cmake")["available"]:
        return {"status": "unavailable", "tool": "cmake",
                "install_hint": detect("cmake")["install_hint"]}
    src = Path(source_dir).resolve()
    bld = Path(build_dir).resolve()
    bld.mkdir(parents=True, exist_ok=True)
    cmd = ["cmake", "-S", str(src), "-B", str(bld)]
    if generator:
        cmd += ["-G", generator]
    cmd += (extra or [])
    return _run(cmd, cwd=src)


def cmake_build(build_dir: str | Path, target: str | None = None,
                jobs: int = 4) -> dict:
    if not detect("cmake")["available"]:
        return {"status": "unavailable", "tool": "cmake"}
    bld = Path(build_dir).resolve()
    cmd = ["cmake", "--build", str(bld), "--parallel", str(jobs)]
    if target:
        cmd += ["--target", target]
    return _run(cmd, cwd=bld)


def make_build(source_dir: str | Path, target: str | None = None,
               jobs: int = 4) -> dict:
    if not detect("make")["available"]:
        return {"status": "unavailable", "tool": "make"}
    src = Path(source_dir).resolve()
    cmd = ["make", "-j", str(jobs)]
    if target:
        cmd.append(target)
    return _run(cmd, cwd=src)


def run_build(system: str, source_dir: str | Path, build_dir: str | Path | None = None,
              target: str | None = None, jobs: int = 4,
              extra: list[str] | None = None) -> dict:
    """Dispatch to the requested build system."""
    system = (system or "").lower()
    if system == "cmake":
        bld = build_dir or (Path(source_dir) / "build")
        cfg = cmake_configure(source_dir, bld, extra=extra)
        if cfg["status"] not in ("ok",):
            return {"configure": cfg, "build": None}
        return {"configure": cfg, "build": cmake_build(bld, target, jobs)}
    if system == "make":
        return {"build": make_build(source_dir, target, jobs)}
    if system == "ninja":
        if not detect("ninja")["available"]:
            return {"status": "unavailable", "tool": "ninja"}
        bld = Path(build_dir or source_dir).resolve()
        return {"build": _run(["ninja"], cwd=bld)}
    return {"status": "error", "message": f"unknown build system: {system}"}
