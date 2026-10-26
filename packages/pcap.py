"""PCAP analysis helpers (D4).

Parses pcap file headers and packet records without external deps;
tshark/scapy are optional enhancements.
"""
from __future__ import annotations

import struct
from pathlib import Path


def parse_pcap(path: str | Path) -> dict:
    data = Path(path).read_bytes()
    if len(data) < 24:
        return {"status": "error", "message": "file too short"}
    magic = data[:4]
    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"
    elif magic == b"\x4d\x3c\xb2\xa1":
        endian = "<"  # nanosecond timestamps
    else:
        return {"status": "error", "message": f"unknown magic {magic.hex()}"}
    # global header: magic(4) vmaj(2) vmin(2) thiszone(4) sigfigs(4) snaplen(4) network(2)
    _magic, vmaj, vmin, _tz, _sig, snaplen, network = struct.unpack(endian + "IHHIIII", data[:24] + b"\x00\x00")
    # Actually network is at offset 20, 4 bytes? pcap global header is 24 bytes: magic 4, vmaj 2, vmin 2, thiszone 4, sigfigs 4, snaplen 4, network 4
    vmaj, vmin, _tz, _sig, snaplen, network = struct.unpack(endian + "HHIIII", data[4:24])
    offset = 24
    packets = 0
    total_bytes = 0
    while offset + 16 <= len(data):
        ts_sec, ts_frac, incl_len, orig_len = struct.unpack(endian + "IIII", data[offset:offset + 16])
        offset += 16
        if offset + incl_len > len(data):
            break
        offset += incl_len
        packets += 1
        total_bytes += orig_len
    return {"status": "ok", "version": f"{vmaj}.{vmin}", "snaplen": snaplen,
            "link_type": network, "packet_count": packets, "total_bytes": total_bytes}


def try_tshark() -> dict:
    import shutil
    exe = shutil.which("tshark")
    if not exe:
        return {"available": False, "install_hint": "apt install tshark / wireshark"}
    return {"available": True, "path": exe}
