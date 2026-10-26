"""CMSIS-SVD register-map parser (D12).

Parses an .svd file into peripherals -> registers -> fields with addresses.
Stdlib xml only; no external deps.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def _text(el, tag, default=None):
    sub = el.find(tag)
    return sub.text.strip() if (sub is not None and sub.text) else default


def _int(val):
    if val is None:
        return None
    val = val.strip()
    if val.lower().startswith("0x"):
        return int(val, 16)
    try:
        return int(val)
    except ValueError:
        return None


def parse_svd(path: str | Path) -> dict:
    tree = ET.parse(str(path))
    root = tree.getroot()
    device = _text(root, "name")
    base = _text(root, "baseAddress") or "0"
    peripherals = []
    for p in root.findall(".//peripheral"):
        pname = _text(p, "name")
        pbase = _int(_text(p, "baseAddress")) or 0
        regs = []
        for r in p.findall(".//register"):
            rname = _text(r, "name")
            offset = _int(_text(r, "addressOffset")) or 0
            size = _int(_text(r, "size"))
            access = _text(r, "access")
            fields = []
            for f in r.findall(".//field"):
                fields.append({
                    "name": _text(f, "name"),
                    "bitOffset": _int(_text(f, "bitOffset")),
                    "bitWidth": _int(_text(f, "bitWidth")),
                    "access": _text(f, "access"),
                    "description": _text(f, "description"),
                })
            regs.append({"name": rname, "offset": offset, "address": pbase + offset,
                        "size": size, "access": access, "fields": fields})
        peripherals.append({"name": pname, "baseAddress": pbase, "registers": regs})
    return {"device": device, "peripheral_count": len(peripherals), "peripherals": peripherals}
