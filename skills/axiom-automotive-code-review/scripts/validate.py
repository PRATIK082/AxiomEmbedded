"""Validate an axiom-automotive-code-review record against the template contract.

Usage: python scripts/validate.py <record.yaml>
Exit 0 when the record satisfies every gate; exit 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required (pip install pyyaml)")
    raise SystemExit(2)


REQUIRED_TOP = ["id", "date", "scope", "module", "standard", "reviewers",
                "sampling", "rule_check", "defects", "verdict", "evidence"]
VERDICTS = {"READY", "REWORK", "BLOCKED"}
SEVERITIES = {"BLOCKED", "REWORK", "ADVISORY"}


def validate(record: dict) -> list[str]:
    errors: list[str] = []
    rev = record.get("review")
    if not isinstance(rev, dict):
        return ["top-level 'review' mapping is required"]
    for key in REQUIRED_TOP:
        if key not in rev:
            errors.append(f"missing required field: review.{key}")
    scope = rev.get("scope", {})
    if isinstance(scope, dict) and not scope.get("files") and not scope.get("change_set"):
        errors.append("review.scope needs 'files' or 'change_set'")
    module = rev.get("module", {})
    if isinstance(module, dict):
        for key in ("id", "autosar_release", "asil_scope"):
            if key not in module:
                errors.append(f"missing required field: review.module.{key}")
    reviewers = rev.get("reviewers", [])
    roles = [r.get("role") for r in reviewers] if isinstance(reviewers, list) else []
    if "author" in roles and len(reviewers) < 2:
        errors.append("author cannot be the sole reviewer")
    if isinstance(module, dict) and module.get("asil_scope") in ("C", "D"):
        if "independent" not in roles:
            errors.append("ASIL C/D scope requires an independent reviewer")
    if rev.get("sampling") == "risk-based" and not rev.get("sampling_rationale"):
        errors.append("risk-based sampling requires sampling_rationale")
    if rev.get("sampling") not in ("full", "risk-based"):
        errors.append("review.sampling must be 'full' or 'risk-based'")
    rule_check = rev.get("rule_check", {})
    if isinstance(rule_check, dict):
        if rule_check.get("unresolved_mandatory", 0) != 0:
            errors.append("unresolved mandatory rule violations must be 0 or verdict cannot be READY")
    defects = rev.get("defects", [])
    if isinstance(defects, list):
        for i, d in enumerate(defects):
            if not isinstance(d, dict):
                errors.append(f"review.defects[{i}] must be a mapping")
                continue
            for key in ("id", "location", "severity", "requirement", "status"):
                if key not in d:
                    errors.append(f"review.defects[{i}] missing '{key}'")
            if d.get("severity") not in SEVERITIES:
                errors.append(f"review.defects[{i}] invalid severity")
    verdict = rev.get("verdict")
    if verdict not in VERDICTS:
        errors.append("review.verdict must be READY, REWORK or BLOCKED")
    if verdict == "READY" and isinstance(defects, list):
        open_blocked = [d for d in defects
                        if isinstance(d, dict) and d.get("severity") == "BLOCKED"
                        and d.get("status") != "waived"]
        if open_blocked:
            errors.append("verdict READY is invalid with open BLOCKED defects")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-2])
        return 2
    path = Path(argv[1])
    try:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse {path}: {exc}")
        return 1
    errors = validate(record if isinstance(record, dict) else {})
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print(f"OK: {path} satisfies the review-record contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
