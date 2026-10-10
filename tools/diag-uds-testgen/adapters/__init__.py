"""Adapter stubs: each converts a native extract into the canonical spec.

Adapters translate only; they never invent SIDs/subfunctions (Rule 5/Rule 7).
Full parsers (ARXML/ODX/CDD/XLSX) are project-provided; these stubs define the
contract and validate row/element error locations.
"""
from __future__ import annotations

VALID_SIDS = {0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x24, 0x27, 0x28, 0x29, 0x2A,
              0x2C, 0x2E, 0x2F, 0x31, 0x34, 0x35, 0x36, 0x37, 0x38, 0x3D, 0x3E,
              0x83, 0x84, 0x85, 0x86, 0x87}


def validate_service_row(sid: int, location: str) -> None:
    if sid not in VALID_SIDS:
        raise ValueError(f"{location}: SID 0x{sid:02X} outside Rule 1 matrix — declare or reject explicitly")


def xlsx_row_to_service(row: dict, row_no: int, source: str) -> dict:
    """Map one validated XLS/XLSX row to a service fragment.

    Expected keys: sid, subfunction|did|dtc|rid, session, security_level, addressing.
    Unknown SIDs raise with file + row number (never silently dropped).
    """
    sid = int(row.get("sid", 0))
    validate_service_row(sid, f"{source} row {row_no}")
    return {"sid": sid, "row": row_no}
