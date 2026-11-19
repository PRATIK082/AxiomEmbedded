"""Bench self-discovery: enumerate host serial candidates and resolve board_config channels.

Usage:
    python scripts/bench_discover.py --discover
    python scripts/bench_discover.py path/to/board_config.yaml

Heuristic, stdlib-only resolution check: file-backed ports by existence,
network instruments by TCP connect with a short timeout. Always exits 0
with a JSON report; unresolved names are findings for pre-check, not
crashes here.
"""
from __future__ import annotations

import glob
import json
import re
import socket
import sys


def discover_ports() -> list[str]:
    found: list[str] = []
    for pat in ("/dev/ttyUSB*", "/dev/ttyACM*", "/dev/ttyAMA*",
                "/dev/serial/by-id/*", "/dev/ttyS*"):
        try:
            found.extend(glob.glob(pat))
        except OSError:
            continue
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"HARDWARE\DEVICEMAP\SERIALCOMM") as key:
                i = 0
                while True:
                    try:
                        _, value, _ = winreg.EnumValue(key, i)
                        found.append(str(value))
                        i += 1
                    except OSError:
                        break
        except OSError:
            pass
    return sorted(set(found))


def parse_channels(text: str) -> dict[str, dict[str, str]]:
    """Regex-extract logical channel targets (stdlib; not a full YAML parse)."""
    channels: dict[str, dict[str, str]] = {}
    in_channels = False
    current: str | None = None
    for line in text.splitlines():
        if re.match(r"^channels\s*:\s*$", line):
            in_channels = True
            continue
        if in_channels and re.match(r"^\S", line):
            break
        m = re.match(r"^\s{2}([A-Z0-9_]+)\s*:\s*(?:\{(.*)\})?\s*$", line)
        if in_channels and m:
            current = m.group(1)
            channels[current] = {}
            inline = m.group(2) or ""
            for key in ("port", "visa", "host", "target"):
                mm = re.search(key + r"\s*:\s*([^,}]+)", inline)
                if mm:
                    channels[current][key] = mm.group(1).strip()
            continue
        m2 = re.match(r"^\s{4}(port|visa|host|target)\s*:\s*(.+?)\s*$", line)
        if in_channels and current and m2:
            channels[current][m2.group(1)] = m2.group(2)
    return channels


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def resolve(channels: dict[str, dict[str, str]]) -> dict[str, dict]:
    import os
    out: dict[str, dict] = {}
    for name, spec in channels.items():
        target = (spec.get("port") or spec.get("visa")
                  or spec.get("host") or spec.get("target") or "")
        kind = "unknown"
        resolved = False
        if target.startswith("TCPIP"):
            kind = "scpi-tcp"
            m = re.search(r"TCPIP\d*::([^:;]+)", target)
            host = m.group(1) if m else ""
            resolved = bool(host) and tcp_reachable(host, 5025)
        elif target.startswith("USB") and "::INSTR" in target:
            kind = "visa-usb"
            resolved = False  # needs VISA runtime; pre-check probes it live
        elif target.startswith("/dev/") or re.match(r"COM\d+", target, re.I):
            kind = "serial"
            resolved = os.path.exists(target)
        elif target:
            kind = "other"
            resolved = False
        out[name] = {"kind": kind, "target": target, "resolved": resolved}
    return out


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--discover":
        print(json.dumps({"discovered_ports": discover_ports()}, indent=2))
        return 0
    if len(argv) != 2:
        print("usage: bench_discover.py (--discover | board_config.yaml)",
              file=sys.stderr)
        return 2
    try:
        text = open(argv[1], encoding="utf-8").read()
    except OSError as exc:
        print(json.dumps({"error": str(exc), "unresolved": ["board_config.yaml unreadable"]}))
        return 0
    channels = parse_channels(text)
    resolved = resolve(channels)
    unresolved = sorted(n for n, r in resolved.items() if not r["resolved"])
    print(json.dumps({"channels": resolved, "unresolved": unresolved,
                      "discovered_ports": discover_ports()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
