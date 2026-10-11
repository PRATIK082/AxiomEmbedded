"""Validate skills catalog + SKILL.md contracts. Exit 1 on any error.

Usage:
  python scripts/validate_skills.py [--skill <id>] [--catalog skills/catalog.yaml]
"""
from __future__ import annotations
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from packages.skills.validator import validate_all


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", default=None)
    ap.add_argument("--catalog", default="skills/catalog.yaml")
    args = ap.parse_args()
    report = validate_all(ROOT / args.catalog)
    rc = 0
    if args.skill:
        items = [r for r in report["skills"] if r["skill"] == args.skill]
        if not items:
            print(f"unknown skill: {args.skill}")
            return 2
        report = {"valid": items[0]["valid"], "skills": items,
                  "catalog": None, "unindexed_in_skill_index": []}
    for r in report["skills"]:
        if args.skill and r["skill"] != args.skill:
            continue
        state = "PASS" if r["valid"] else "FAIL"
        print(f"{r['skill']}: {state}")
        for e in r["errors"]:
            print(f"  error: {e}")
            rc = 1
        for w_ in r["warnings"]:
            print(f"  warn: {w_}")
    if report.get("catalog") and not args.skill:
        c = report["catalog"]
        print(f"catalog: {'PASS' if c['valid'] else 'FAIL'} "
              f"({c['skill_count']} skills)")
        for e in c["errors"]:
            print(f"  error: {e}")
            rc = 1
        for w_ in c["warnings"]:
            print(f"  warn: {w_}")
    if report.get("unindexed_in_skill_index"):
        print("note: unindexed in skill-index.json "
              f"(registry sync pending): {len(report['unindexed_in_skill_index'])}")
    print("VALIDATION: " + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
