"""External binary detectors: is the wrapped tool actually installed here?

Design rule (standalone-independence P2): Axiom wraps best-in-class OSS tools,
never reimplements them. These detectors probe PATH for the wrapped binaries
so `axiom packs` can tell the operator what is ready vs what to install.
Pure stdlib (shutil/subprocess); a missing binary is `available: False`,
never an error.
"""

from __future__ import annotations

import shutil
import subprocess

# binary -> {version_arg, kind, install_hint}. Order is display order.
DETECTORS: dict[str, dict] = {
    "cppcheck": {
        "kind": "static-analysis",
        "version_arg": "--version",
        "install_hint": "winget install Cppcheck / choco install cppcheck / apt install cppcheck",
    },
    "clang-tidy": {
        "kind": "static-analysis",
        "version_arg": "--version",
        "install_hint": "LLVM release bundle or: apt install clang-tidy",
    },
    "ceedling": {
        "kind": "unit-test",
        "version_arg": "version",
        "install_hint": "gem install ceedling (Unity/CMock bundled)",
    },
    "gcovr": {
        "kind": "coverage",
        "version_arg": "--version",
        "install_hint": "pip install gcovr (needs gcc/gcov underneath)",
    },
    "lcov": {
        "kind": "coverage",
        "version_arg": "--version",
        "install_hint": "apt install lcov / choco install lcov",
    },
    "robot": {
        "kind": "system-test",
        "version_arg": "--version",
        "install_hint": "pip install robotframework",
    },
    "renode": {
        "kind": "simulation",
        "version_arg": "--version",
        "install_hint": "Antmicro Renode release (MIT): renode.io",
    },
    "qemu-system-arm": {
        "kind": "simulation",
        "version_arg": "--version",
        "install_hint": "winget install QEMU / apt install qemu-system-arm",
    },
    "openocd": {
        "kind": "debug-probe",
        "version_arg": "--version",
        "install_hint": "apt install openocd / xpack-openocd release",
    },
}


def detect(binary: str) -> dict:
    """Probe one binary. Never raises: unknown binaries report unavailable."""
    spec = DETECTORS.get(binary, {})
    path = shutil.which(binary)
    if not path:
        return {"binary": binary, "available": False, "path": None,
                "version": None, "install_hint": spec.get("install_hint", "")}
    version: str | None = None
    try:
        proc = subprocess.run(
            [path, spec.get("version_arg", "--version")],
            capture_output=True, text=True, timeout=15)
        out = (proc.stdout or proc.stderr or "").strip().splitlines()
        version = out[0][:120] if out else None
    except Exception:
        version = None
    return {"binary": binary, "available": True, "path": path,
            "version": version, "install_hint": ""}


def detect_all() -> dict:
    """Probe every known binary. Keys are binary names."""
    return {name: detect(name) for name in DETECTORS}
