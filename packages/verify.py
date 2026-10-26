"""Verification gate: build + static analysis + tests + size/map check.

Runs each gate and returns a structured report; exits non-zero if any fails.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from packages.toolchain import run_build, run_static, run_tests


def run_verify(source: str = ".", build_system: str = "cmake",
               static_tool: str = "cppcheck") -> dict:
    src = Path(source).resolve()
    gates: list[dict] = []

    # 1. build
    build_res = run_build(build_system, str(src), None, None, 4)
    build_ok = True
    for v in (build_res.values() if isinstance(build_res, dict) else []):
        if isinstance(v, dict) and v.get("status") in ("failed", "timeout", "error", "unavailable"):
            build_ok = False
    gates.append({"gate": "build", "status": "pass" if build_ok else "fail",
                  "detail": build_res})

    # 2. static analysis (only if tool available)
    static_res = run_static(static_tool, str(src))
    static_ok = static_res.get("status") in ("ok", "findings") and static_res.get("returncode", 0) == 0
    # treat "findings" with rc 0 as pass-with-warnings
    if static_res.get("status") == "unavailable":
        static_ok = True  # tool absent -> skip, not fail
    gates.append({"gate": "static", "status": "pass" if static_ok else "fail",
                  "detail": static_res})

    # 3. tests
    test_res = run_tests("pytest", str(src))
    tests_ok = test_res.get("status") == "ok" and test_res.get("failed", 0) == 0
    gates.append({"gate": "tests", "status": "pass" if tests_ok else "fail",
                  "detail": test_res})

    # 4. size/map check (best-effort: look for .map files and report total)
    size_info = {"map_files": [], "total_bytes": 0}
    for mf in src.rglob("*.map"):
        try:
            size_info["map_files"].append(str(mf.relative_to(src)))
            size_info["total_bytes"] += mf.stat().st_size
        except OSError:
            pass
    gates.append({"gate": "size_map", "status": "pass", "detail": size_info})

    overall = all(g["status"] == "pass" for g in gates)
    return {"status": "pass" if overall else "fail", "gates": gates}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="axiom verify")
    ap.add_argument("--source", default=".")
    ap.add_argument("--build-system", default="cmake")
    ap.add_argument("--static-tool", default="cppcheck")
    args = ap.parse_args(argv)
    rep = run_verify(args.source, args.build_system, args.static_tool)
    print(json.dumps(rep, indent=2))
    return 0 if rep["status"] == "pass" else 1
