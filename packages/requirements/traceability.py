"""Traceability matrix generation: req <-> code <-> test."""
from __future__ import annotations

import csv
import re
from pathlib import Path


def generate_matrix(requirements: list[dict], test_files: list[str] | None = None,
                    source_files: list[str] | None = None) -> list[dict]:
    """Build a list of rows {requirement, code_refs, test_refs}.

    Code/test refs are found by searching source for the requirement id token.
    """
    test_files = test_files or []
    source_files = source_files or []
    rows = []
    for r in requirements:
        rid = r.get("id", "")
        code_refs = [f for f in source_files if _contains(f, rid)]
        test_refs = [f for f in test_files if _contains(f, rid)]
        rows.append({"requirement": rid, "title": r.get("title", ""),
                     "code_refs": code_refs, "test_refs": test_refs,
                     "status": "covered" if test_refs else "uncovered"})
    return rows


def _contains(path: str, token: str) -> bool:
    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return bool(token) and token in text


def write_matrix_csv(rows: list[dict], output: str | Path) -> Path:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["requirement", "title", "code_refs", "test_refs", "status"])
        for r in rows:
            w.writerow([r["requirement"], r["title"],
                        ";".join(r["code_refs"]), ";".join(r["test_refs"]), r["status"]])
    return out
