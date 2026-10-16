# SPDX-License-Identifier: Apache-2.0
"""Assurance engines: artifact validation, traceability check, review build.

Stdlib + PyYAML only. Deterministic, no hidden state. Original AxiomEmbedded logic.
"""
from __future__ import annotations

import datetime as _dt
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]

ENVELOPE_REQUIRED = ["artifact_id", "schema_version", "kind", "status", "domain",
                     "created_at", "updated_at", "author", "approval_status"]
STATUS_ENUM = {"draft", "in-review", "approved", "superseded"}
APPROVAL_ENUM = {"draft", "pending-review", "approved", "rejected"}
SEVERITIES = {"Blocker", "Major", "Minor", "Observation", "Information Request"}
ID_RES = {
    "REQ-": re.compile(r"^REQ-[0-9]+$"),
    "HAZ-": re.compile(r"^HAZ-[0-9]+$"),
    "TEST-": re.compile(r"^TEST-[0-9]+$"),
    "SEC-": re.compile(r"^SEC-[0-9]+$"),
    "CTL-": re.compile(r"^CTL-[0-9]+$"),
    "EVD-": re.compile(r"^EVD-[0-9]+$"),
    "REV-": re.compile(r"^REV-[0-9]+$"),
}
KIND_FILES = {
    "system-scope": "assurance-scope.schema.json",
    "hazard-risk": "assurance-hazard-risk.schema.json",
    "safety-requirements": "assurance-safety-requirements.schema.json",
    "vnv-plan": "assurance-vnv-plan.schema.json",
    "threat-model": "assurance-threat-model.schema.json",
    "review-report": "assurance-review.schema.json",
}


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_dt(value: str) -> bool:
    try:
        _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def load_doc(path: pathlib.Path) -> dict:
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")) or {}


def validate_artifact(doc: dict) -> list[str]:
    """Validate envelope + kind body + ID/date/enum rules. Returns error list."""
    errors: list[str] = []
    for key in ENVELOPE_REQUIRED:
        if key not in doc:
            errors.append(f"missing field: {key}")
    if doc.get("status") not in STATUS_ENUM:
        errors.append(f"bad status {doc.get('status')!r}")
    if doc.get("approval_status") not in APPROVAL_ENUM:
        errors.append(f"bad approval_status {doc.get('approval_status')!r}")
    for field in ("created_at", "updated_at"):
        if field in doc and not _parse_dt(doc[field]):
            errors.append(f"bad {field} {doc[field]!r} (want UTC ISO 8601)")
    kind = doc.get("kind")
    if kind not in KIND_FILES:
        errors.append(f"unknown kind {kind!r}")
        return errors
    bodies = {"system-scope": ("system", "operating_context", "boundaries"),
              "hazard-risk": ("hazards",), "safety-requirements": ("requirements",),
              "vnv-plan": ("test_cases", "trace_matrix"),
              "threat-model": ("threats",), "review-report": ("target_artifact", "verdict", "findings")}
    for field in bodies[kind]:
        if field not in doc:
            errors.append(f"{kind}: missing field {field}")
    # ID-format spot checks
    for prefix, rx in ID_RES.items():
        for collection in ("hazards", "requirements", "test_cases", "threats", "findings"):
            items = doc.get(collection) or []
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and str(item.get("id", "")).startswith(prefix):
                        if not rx.match(str(item["id"])):
                            errors.append(f"bad id {item['id']!r}")
    # duplicate IDs within artifact
    seen: dict[str, str] = {}
    for collection in ("hazards", "requirements", "test_cases", "threats"):
        for item in doc.get(collection) or []:
            if isinstance(item, dict) and "id" in item:
                if item["id"] in seen:
                    errors.append(f"duplicate id {item['id']!r}")
                seen[item["id"]] = collection
    # high-severity hazard must carry a control or rationale
    for hazard in doc.get("hazards") or []:
        if isinstance(hazard, dict) and hazard.get("severity") in ("high", "critical"):
            if not hazard.get("controls") and not hazard.get("rationale"):
                errors.append(f"{hazard.get('id', '?')}: high-severity hazard without control or rationale")
    # review blockers need recommendations
    for finding in doc.get("findings") or []:
        if isinstance(finding, dict) and finding.get("severity") == "Blocker":
            if not finding.get("recommendation"):
                errors.append(f"{finding.get('id', '?')}: Blocker without recommendation")
        if isinstance(finding, dict) and finding.get("severity") not in SEVERITIES:
            errors.append(f"bad severity {finding.get('severity')!r}")
    return errors


def validate_artifact_file(path: str | pathlib.Path) -> dict:
    doc = load_doc(pathlib.Path(path))
    errors = validate_artifact(doc)
    return {"file": str(path), "valid": not errors, "errors": errors,
            "kind": doc.get("kind"), "artifact_id": doc.get("artifact_id")}


def collect_artifacts(directory: str | pathlib.Path) -> list[dict]:
    out = []
    base = pathlib.Path(directory)
    for path in sorted(base.rglob("*.yaml")) + sorted(base.rglob("*.yml")):
        try:
            doc = load_doc(path)
        except Exception:
            continue
        if isinstance(doc, dict) and doc.get("kind") in KIND_FILES:
            out.append({"path": str(path), "doc": doc})
    return out


def check_traceability(directory: str | pathlib.Path) -> dict:
    """Cross-artifact trace checks. Returns {valid, errors, warnings, counts}."""
    arts = collect_artifacts(directory)
    errors: list[str] = []
    warnings: list[str] = []
    reqs: dict[str, str] = {}
    hazards: dict[str, dict] = {}
    tests: dict[str, dict] = {}
    threats: dict[str, dict] = {}
    for art in arts:
        doc = art["doc"]
        for item in doc.get("requirements") or []:
            if isinstance(item, dict) and "id" in item:
                if item["id"] in reqs:
                    errors.append(f"duplicate requirement id {item['id']}")
                reqs[item["id"]] = art["path"]
        for item in doc.get("hazards") or []:
            if isinstance(item, dict) and "id" in item:
                hazards[item["id"]] = item
        for item in doc.get("test_cases") or []:
            if isinstance(item, dict) and "id" in item:
                tests[item["id"]] = item
        for item in doc.get("threats") or []:
            if isinstance(item, dict) and "id" in item:
                threats[item["id"]] = item
    covered_reqs: set[str] = set()
    for art in arts:
        for item in art["doc"].get("test_cases") or []:
            if isinstance(item, dict):
                for req in item.get("covers_requirements") or []:
                    covered_reqs.add(req)
                    if req not in reqs:
                        errors.append(f"{item.get('id', '?')}: covers unknown requirement {req}")
        for row in art["doc"].get("trace_matrix") or []:
            if isinstance(row, dict):
                covered_reqs.add(row.get("requirement", ""))
    for rid in sorted(reqs):
        if rid not in covered_reqs:
            errors.append(f"orphan requirement {rid}: no test case covers it")
    for hid, hazard in sorted(hazards.items()):
        if hazard.get("severity") in ("high", "critical") and not hazard.get("controls") \
                and not hazard.get("rationale"):
            errors.append(f"hazard {hid}: high severity without control or rationale")
    for tid, threat in sorted(threats.items()):
        if not threat.get("controls"):
            warnings.append(f"threat {tid}: no controls recorded (OPEN accepted if explicit)")
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "counts": {"requirements": len(reqs), "hazards": len(hazards),
                       "tests": len(tests), "threats": len(threats),
                       "artifacts": len(arts)}}


def build_review(target_artifact_id: str, findings: list[dict], reviewer: str = "independent-reviewer",
                 domain: str = "industrial") -> dict:
    """Build an append-only review report dict (never mutates the target)."""
    blockers = sum(1 for f in findings if f.get("severity") == "Blocker")
    verdict = "revise-and-resubmit" if blockers else (
        "accept-with-actions" if findings else "accept")
    now = utcnow()
    return {
        "artifact_id": f"REV-{target_artifact_id}",
        "schema_version": "1.0.0",
        "kind": "review-report",
        "status": "draft",
        "domain": domain,
        "standards": [],
        "created_at": now,
        "updated_at": now,
        "author": reviewer,
        "reviewer": reviewer,
        "assumptions": [],
        "evidence": [target_artifact_id],
        "traceability": [{"source": f"REV-{target_artifact_id}", "target": target_artifact_id,
                           "relationship": "reviews"}],
        "open_questions": [],
        "approval_status": "pending-review",
        "target_artifact": target_artifact_id,
        "verdict": verdict,
        "findings": findings,
    }
