"""CAN bus helpers: DBC parsing, message decoding (python-can optional)."""
from __future__ import annotations

import re
from pathlib import Path

# Minimal DBC parser: extracts BO_ (message) and SG_ (signal) lines.
MSG_RE = re.compile(r"^BO_\s+(\d+)\s+(\w+)\s*:\s*(\d+)\s+(\w+)")
SIG_RE = re.compile(r"^\s*SG_\s+(\w+)\s*:\s*(\d+)\|(\d+)@([01])([+-])\s*\(\s*([\d.eE+-]+)\s*,\s*([\d.eE+-]+)\s*\)\s*\[\s*([\d.eE+-]+)\s*\|\s*([\d.eE+-]+)\s*\]\s*\"([^\"]*)\"\s*(.*)")


def parse_dbc(path: str | Path) -> dict:
    messages = {}
    current = None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = MSG_RE.match(line.strip())
        if m:
            mid, name, dlc, node = m.groups()
            current = {"id": int(mid), "name": name, "dlc": int(dlc), "node": node, "signals": {}}
            messages[int(mid)] = current
            continue
        sm = SIG_RE.match(line)
        if sm and current is not None:
            name, start, length, endian, sign, factor, offset, mn, mx, unit, receivers = sm.groups()
            current["signals"][name] = {
                "start_bit": int(start), "length": int(length), "endian": endian,
                "signed": sign == "-", "factor": float(factor), "offset": float(offset),
                "min": float(mn), "max": float(mx), "unit": unit,
                "receivers": [r.strip() for r in receivers.split(",") if r.strip()],
            }
    return {"messages": messages, "message_count": len(messages)}


def decode_signal(raw: int, sig: dict) -> float:
    val = raw
    if sig.get("signed") and val >= (1 << (sig["length"] - 1)):
        val -= (1 << sig["length"])
    return val * sig["factor"] + sig["offset"]


def try_python_can() -> dict:
    try:
        import can  # type: ignore
        return {"available": True, "version": getattr(can, "__version__", "unknown")}
    except Exception as exc:
        return {"available": False, "install_hint": "pip install python-can", "error": str(exc)}
