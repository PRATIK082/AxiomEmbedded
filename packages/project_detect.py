# SPDX-License-Identifier: Apache-2.0
"""Detect a project's domain/platform/os from its own files (deterministic).

No network, no model, no content beyond small bounded sniffs of text files.
Signals are filename/extension markers plus a few first-bytes keyword checks.
Output feeds `engage()` so skill selection can be fully automatic:

    detect_project(path) -> engage(domain, platform)

Safety: capped file walk (default 2000 files), skips hidden dirs and known
binary extensions, reads at most 4 KiB of small text files.
"""

from __future__ import annotations

import pathlib

MAX_FILES = 2000
MAX_SNIFF_BYTES = 4096

SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", "node_modules",
             ".venv", "venv", "build", "out", "target", ".axiom"}
SKIP_EXTS = {".o", ".a", ".so", ".elf", ".bin", ".hex", ".png", ".jpg",
             ".pdf", ".zip", ".gz", ".mf4", ".blf", ".asc"}

# (marker-kind, marker, domain, platform, os, weight)
SIGNALS: list[tuple[str, str, str | None, str | None, str | None, int]] = [
    ("ext", ".arxml", "automotive", "autosar-classic", None, 5),
    ("ext", ".dbc", "automotive", "mcu", None, 5),
    ("ext", ".dbf", "automotive", "mcu", None, 4),
    ("ext", ".cdd", "automotive", None, None, 4),
    ("ext", ".odx", "automotive", None, None, 4),
    ("ext", ".a2l", "automotive", None, None, 4),
    ("ext", ".bswmd", "automotive", "autosar-classic", None, 5),
    ("name", "package.xml", "robotics", "ros2", None, 5),
    ("ext", ".urdf", "robotics", "ros2", None, 4),
    ("ext", ".xacro", "robotics", "ros2", None, 4),
    ("ext", ".msg", "robotics", "ros2", None, 2),
    ("name", "CMakeLists.txt", None, None, None, 0),  # sniffed below
    ("ext", ".ioc", None, "mcu", None, 3),
    ("ext", ".ld", None, "mcu", "bare-metal", 3),
    ("ext", ".sv", "industrial", None, None, 3),
    ("ext", ".vhd", "industrial", None, None, 3),
    ("ext", ".v", "industrial", None, None, 1),
    ("ext", ".aadl", "aerospace", None, None, 5),
    ("ext", ".c", None, "mcu", None, 1),
    ("ext", ".h", None, "mcu", None, 1),
]

# keyword (in CMakeLists.txt / Kconfig / README, first 4 KiB) -> facets
CONTENT_SIGNALS: list[tuple[str, str | None, str | None, str | None, int]] = [
    ("ament_cmake", "robotics", "ros2", None, 4),
    ("rclcpp", "robotics", "ros2", None, 4),
    ("FreeRTOS", None, "rtos", "rtos", 4),
    ("Zephyr", None, "rtos", "rtos", 4),
    ("AUTOSAR", "automotive", "autosar-classic", None, 3),
    ("ara::com", "automotive", "autosar-adaptive", "linux", 4),
    ("STM32", None, "mcu", "bare-metal", 2),
    ("MISRA", "automotive", None, None, 2),
    ("DO-178", "aerospace", None, None, 4),
    ("IEC 61508", "industrial", None, None, 3),
    ("IEC61131", "industrial", None, None, 4),
    ("OPC UA", "industrial", None, None, 3),
]


def _iter_files(root: pathlib.Path):
    seen = 0
    stack = [root]
    while stack and seen < MAX_FILES:
        cur = stack.pop()
        try:
            entries = sorted(cur.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.name in SKIP_DIRS or e.name.startswith("."):
                continue
            if e.is_dir():
                stack.append(e)
            elif e.is_file() and e.suffix.lower() not in SKIP_EXTS:
                seen += 1
                if seen > MAX_FILES:
                    return
                yield e


def detect_project(path: str | pathlib.Path = ".") -> dict:
    """Return {domain, platform, os, confidence, signals, scores}."""
    root = pathlib.Path(path).resolve()
    if not root.is_dir():
        return {"status": "error", "message": f"project not found: {path}"}
    dom: dict[str, int] = {}
    plat: dict[str, int] = {}
    oss: dict[str, int] = {}
    signals: list[dict] = []

    def vote(d, p, o, w, why):
        if d:
            dom[d] = dom.get(d, 0) + w
        if p:
            plat[p] = plat.get(p, 0) + w
        if o:
            oss[o] = oss.get(o, 0) + w
        if w:
            signals.append(why)

    for f in _iter_files(root):
        rel = str(f.relative_to(root))
        for kind, marker, d, p, o, w in SIGNALS:
            hit = (f.name == marker) if kind == "name" else (f.suffix.lower() == marker)
            if hit and w:
                vote(d, p, o, w, {"file": rel, "marker": marker,
                                  "domain": d, "platform": p})
        if f.name in ("CMakeLists.txt", "Kconfig", "README.md", "README.rst",
                      "platformio.ini", ".platformio.ini") or f.suffix.lower() in (".cmake",):
            try:
                if f.stat().st_size > 65536:
                    continue
                head = f.read_text(encoding="utf-8", errors="ignore")[:MAX_SNIFF_BYTES]
            except OSError:
                continue
            for kw, d, p, o, w in CONTENT_SIGNALS:
                if kw.lower() in head.lower():
                    vote(d, p, o, w, {"file": rel, "marker": f"content:{kw}",
                                      "domain": d, "platform": p})

    def best(scores):
        if not scores:
            return None, 0.0
        top = max(scores, key=scores.get)
        total = sum(scores.values())
        return top, round(scores[top] / total, 2) if total else 0.0

    domain, dconf = best(dom)
    platform, _ = best(plat)
    os_, _ = best(oss)
    return {"status": "ok", "path": str(root), "domain": domain,
            "platform": platform, "os": os_, "confidence": dconf,
            "scores": {"domain": dom, "platform": plat, "os": oss},
            "signals": signals[:50], "signal_count": len(signals)}
