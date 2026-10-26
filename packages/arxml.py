"""ARXML (AUTOSAR XML) basic validator (D13).

Validates well-formedness and presence of expected AUTOSAR top-level
elements; full XSD validation is out of scope (documented).
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

AUTOSAR_NS = "{http://autosar.org/schema/r4.0}"


def validate_arxml(path: str | Path) -> dict:
    p = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        tree = ET.parse(str(p))
    except ET.ParseError as exc:
        return {"valid": False, "errors": [f"XML parse error: {exc}"], "warnings": []}
    root = tree.getroot()
    # AUTOSAR files typically root <AUTOSAR> or <ar:...>
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag.lower() not in ("autosar",):
        warnings.append(f"root element is {tag!r}, expected AUTOSAR")
    # collect top-level short-names
    short_names = [el.text for el in root.iter() if el.tag.endswith("SHORT-NAME")]
    if not short_names:
        warnings.append("no SHORT-NAME elements found")
    # check for any AR-PACKAGE
    packages = [el for el in root.iter() if el.tag.endswith("AR-PACKAGE")]
    if not packages:
        warnings.append("no AR-PACKAGE elements found")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings,
            "root": tag, "package_count": len(packages),
            "short_name_count": len(short_names)}
