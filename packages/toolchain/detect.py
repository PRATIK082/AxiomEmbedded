"""Embedded toolchain detection: compilers, build systems, probes.

Wraps best-in-class OSS tools (never reimplements). Probes PATH; a missing
binary is available=False, never an error.
"""
from __future__ import annotations

import shutil
import subprocess

# binary -> {kind, version_arg, install_hint}
TOOLCHAINS: dict[str, dict] = {
    "arm-none-eabi-gcc": {"kind": "compiler", "version_arg": "--version",
        "install_hint": "Arm GNU Toolchain (arm-none-eabi)"},
    "arm-none-eabi-g++": {"kind": "compiler", "version_arg": "--version",
        "install_hint": "Arm GNU Toolchain (arm-none-eabi)"},
    "clang": {"kind": "compiler", "version_arg": "--version",
        "install_hint": "LLVM release bundle"},
    "gcc": {"kind": "compiler", "version_arg": "--version",
        "install_hint": "build-essential / MinGW"},
    "g++": {"kind": "compiler", "version_arg": "--version",
        "install_hint": "build-essential / MinGW"},
    "cmake": {"kind": "build-system", "version_arg": "--version",
        "install_hint": "https://cmake.org/download/"},
    "ninja": {"kind": "build-system", "version_arg": "--version",
        "install_hint": "pip install ninja / package manager"},
    "make": {"kind": "build-system", "version_arg": "--version",
        "install_hint": "build-essential / make"},
    "west": {"kind": "build-system", "version_arg": "--version",
        "install_hint": "pip install west (Zephyr)"},
    "pio": {"kind": "build-system", "version_arg": "--version",
        "install_hint": "pip install platformio"},
    "openocd": {"kind": "probe", "version_arg": "--version",
        "install_hint": "apt install openocd / xpack-openocd"},
    "JLinkExe": {"kind": "probe", "version_arg": "-? ",  # J-Link prints on -? with exit 1
        "install_hint": "SEGGER J-Link software pack"},
    "qemu-system-arm": {"kind": "simulator", "version_arg": "--version",
        "install_hint": "apt install qemu-system-arm"},
    "renode": {"kind": "simulator", "version_arg": "--version",
        "install_hint": "Antmicro Renode release"},
    "gcovr": {"kind": "coverage", "version_arg": "--version",
        "install_hint": "pip install gcovr"},
    "cppcheck": {"kind": "static-analysis", "version_arg": "--version",
        "install_hint": "apt install cppcheck"},
    "clang-tidy": {"kind": "static-analysis", "version_arg": "--version",
        "install_hint": "LLVM release bundle"},
}


def detect(name: str) -> dict:
    spec = TOOLCHAINS.get(name, {})
    path = shutil.which(name)
    if not path:
        return {"name": name, "available": False, "path": None,
                "version": None, "kind": spec.get("kind", "unknown"),
                "install_hint": spec.get("install_hint", "")}
    version = None
    try:
        proc = subprocess.run([path, spec.get("version_arg", "--version")],
                              capture_output=True, text=True, timeout=15)
        out = (proc.stdout or proc.stderr or "").strip().splitlines()
        version = out[0][:120] if out else None
    except Exception:
        version = None
    return {"name": name, "available": True, "path": path, "version": version,
            "kind": spec.get("kind", "unknown"), "install_hint": ""}


def detect_all() -> dict[str, dict]:
    return {name: detect(name) for name in TOOLCHAINS}


def available_toolchains() -> list[str]:
    return [n for n, d in detect_all().items() if d["available"]]
