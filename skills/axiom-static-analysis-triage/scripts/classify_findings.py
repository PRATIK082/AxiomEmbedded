"""Deterministic static-analysis findings classifier (axiom-static-analysis-triage).

Reads a findings CSV (finding_id,file,line,rule,severity,message) and an optional
baseline CSV of finding_ids, then buckets each row as new/fixed/carried and maps
severity text to a gate class (blocker/major/minor). Byte-identical output for
identical input (sorted rows, no timestamps).

Usage:
  python scripts/classify_findings.py findings.csv [--baseline base.csv] [--output triage.csv]
"""
from __future__ import annotations
import argparse
import csv
import pathlib
import sys


def gate_class(severity: str) -> str:
    s = (severity or "").strip().lower()
    if s in ("error", "required", "mandatory", "blocker", "high"):
        return "blocker"
    if s in ("warning", "advisory", "medium"):
        return "major"
    return "minor"


def classify(findings_p: pathlib.Path, baseline_p: pathlib.Path | None) -> list[dict]:
    base_ids: set[str] = set()
    if baseline_p and baseline_p.exists():
        with baseline_p.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("finding_id"):
                    base_ids.add(row["finding_id"].strip())
    rows: list[dict] = []
    with findings_p.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            fid = (row.get("finding_id") or "").strip()
            if not fid:
                continue
            rows.append({
                "finding_id": fid,
                "file": (row.get("file") or "").strip(),
                "line": (row.get("line") or "").strip(),
                "rule": (row.get("rule") or "").strip(),
                "severity": (row.get("severity") or "").strip(),
                "gate_class": gate_class(row.get("severity")),
                "bucket": "new" if fid not in base_ids else "carried",
                "disposition": "",
            })
    rows.sort(key=lambda r: r["finding_id"])
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("findings")
    ap.add_argument("--baseline", default=None)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    rows = classify(pathlib.Path(args.findings),
                     pathlib.Path(args.baseline) if args.baseline else None)
    dest = pathlib.Path(args.output) if args.output else None
    fh = dest.open("w", newline="", encoding="utf-8") if dest else sys.stdout
    try:
        w = csv.DictWriter(fh, fieldnames=["finding_id", "file", "line", "rule",
                                           "severity", "gate_class", "bucket",
                                           "disposition"])
        w.writeheader()
        w.writerows(rows)
    finally:
        if dest:
            fh.close()
    print(f"classified {len(rows)} findings "
          f"({sum(1 for r in rows if r['bucket'] == 'new')} new)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
