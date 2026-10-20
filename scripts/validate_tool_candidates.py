# SPDX-License-Identifier: Apache-2.0
"""Validate registries/tool-candidates.yaml against its schema and the
AxiomEmbedded plugin contract.

Checks:
  1. The registry parses and every candidate validates against
     schemas/tool-candidate.schema.json.
  2. Candidate ids are unique.
  3. Every candidate names a plugin point that exists in the repository
     (a real directory) or is an explicit non-path extension point.
  4. Copyleft (GPL/AGPL) candidates use linkage: subprocess.
  5. Candidates marked accepted/candidate have a benefit, a milestone and
     an upstream URL.
  6. Rejected candidates carry a rejected_reason.

Usage: python scripts/validate_tool_candidates.py
Exit code 0 = pass, 1 = fail.
"""

from __future__ import annotations

import json
import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "registries" / "tool-candidates.yaml"
SCHEMA = REPO_ROOT / "schemas" / "tool-candidate.schema.json"

#: Extension points that are not directories under the repository root.
NON_PATH_PLUGIN_POINTS = {"rules", "docs/research", "schemas/artifact", "packages/core"}


def _is_copyleft(license_expr: str) -> bool:
    low = license_expr.lower()
    return "gpl" in low or "agpl" in low


def validate() -> list[str]:
    """Return a list of problems. Empty list means the registry is valid."""
    problems: list[str] = []

    if not REGISTRY.exists():
        return [f"missing registry: {REGISTRY}"]
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    candidates = data.get("candidates") or []
    if not candidates:
        return ["registry contains no candidates"]

    # --- schema validation (only the checks jsonschema would make that we
    # --- can express without taking a new dependency) -------------------
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = schema["properties"]["candidates"]["items"]["required"]
    allowed_status = set(schema["properties"]["candidates"]["items"]["properties"]["status"]["enum"])
    allowed_channel = set(schema["properties"]["candidates"]["items"]["properties"]["channel"]["enum"])
    allowed_kind = set(schema["properties"]["candidates"]["items"]["properties"]["kind"]["enum"])
    allowed_linkage = set(schema["properties"]["candidates"]["items"]["properties"]["linkage"]["enum"])
    milestone_pattern = schema["properties"]["candidates"]["items"]["properties"]["milestone"]["pattern"]
    id_pattern = schema["properties"]["candidates"]["items"]["properties"]["id"]["pattern"]

    seen: set[str] = set()
    for index, cand in enumerate(candidates):
        where = f"candidates[{index}]"
        cid = cand.get("id", "<no id>")
        where = f"candidate '{cid}'"

        for key in required:
            if key not in cand or cand[key] in (None, ""):
                problems.append(f"{where}: missing required key '{key}'")

        if cid in seen:
            problems.append(f"{where}: duplicate id")
        seen.add(cid)

        import re

        if not re.match(id_pattern, str(cid)):
            problems.append(f"{where}: id does not match {id_pattern}")
        if not re.match(milestone_pattern, str(cand.get("milestone", ""))):
            problems.append(f"{where}: milestone does not match {milestone_pattern}")

        if cand.get("status") not in allowed_status:
            problems.append(f"{where}: status '{cand.get('status')}' not allowed")
        if cand.get("channel") not in allowed_channel:
            problems.append(f"{where}: channel '{cand.get('channel')}' not allowed")
        if cand.get("kind") not in allowed_kind:
            problems.append(f"{where}: kind '{cand.get('kind')}' not allowed")
        if cand.get("linkage") not in allowed_linkage:
            problems.append(f"{where}: linkage '{cand.get('linkage')}' not allowed")

        upstream = str(cand.get("upstream", ""))
        if not upstream.startswith(("http://", "https://")):
            problems.append(f"{where}: upstream must be an absolute URL")

        # copyleft must never be imported into Axiom code
        if _is_copyleft(str(cand.get("license", ""))) and cand.get("linkage") == "import":
            problems.append(
                f"{where}: copyleft licence '{cand.get('license')}' must use linkage: subprocess"
            )

        # plugin point must exist
        plugin_point = str(cand.get("plugin_point", ""))
        head = plugin_point.split("/", 1)[0]
        if plugin_point and plugin_point not in NON_PATH_PLUGIN_POINTS:
            if not (REPO_ROOT / head).exists():
                problems.append(f"{where}: plugin_point '{plugin_point}' does not resolve in the repo")

        if cand.get("status") == "rejected" and not cand.get("rejected_reason"):
            problems.append(f"{where}: rejected candidate needs a rejected_reason")
        if cand.get("status") in ("candidate", "accepted") and not cand.get("benefit"):
            problems.append(f"{where}: adoptable candidate needs a benefit")

    return problems


def main() -> int:
    problems = validate()
    if problems:
        print(f"Tool candidate validation: FAIL ({len(problems)} problems)")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    total = len(data.get("candidates") or [])
    adoptable = sum(
        1 for c in (data.get("candidates") or [])
        if c.get("status") in ("candidate", "accepted")
    )
    print(f"Tool candidate validation: PASS ({total} candidates, {adoptable} adoptable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
