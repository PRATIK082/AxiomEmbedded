"""Scaffold a new axiom-* skill. Dry-run by default.

Usage:
  python scripts/create_skill.py --id axiom-<domain>-<cap> --title "..." [--domain automotive] [--apply]
"""
from __future__ import annotations
import argparse
import pathlib
import re
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^axiom-[a-z0-9]+(-[a-z0-9]+)+$")


def _catalog_entry(skill_id, title, domain):
    return {
        "id": skill_id,
        "name": skill_id,
        "title": title,
        "version": "1.2.0",
        "domain": domain,
        "subdomain": domain,
        "category": "implementation",
        "maturity": "experimental",
        "owner": "axiom-embedded",
        "tags": ["skill"],
        "inputs": ["repository path", "objective"],
        "outputs": ["report"],
        "dependencies": [],
        "related_skills": [],
        "path": f"skills/{skill_id}",
        "enabled": True,
        "sub_skills": [],
    }


def scaffold(skill_id: str, title: str, domain: str, apply: bool = False) -> list[str]:
    if not ID_RE.match(skill_id):
        raise ValueError(f"skill id must match {ID_RE.pattern}: {skill_id!r}")
    d = ROOT / "skills" / skill_id
    if (d / "SKILL.md").exists():
        raise FileExistsError(f"skill exists: {skill_id}")
    short = skill_id.replace("axiom-", "").replace("-", ".")
    fm = (f"name: {skill_id}\ntitle: {title}\ndescription: >\n"
          f"  {title} workflow for {domain}. Use when {title.lower()} tasks arise in {domain} projects.\n"
          f"version: 1.2.0\nauthor: PRATIK082\nlicense: Apache-2.0\n"
          f"domains: [{domain}]\nplatforms: [mcu]\naxiom:\n"
          f"  dotted_name: axiom.{domain}.{short}\n  domain: {domain}\n"
          f"  maturity: experimental\n  review_required: true\n  safety_critical: false\n"
          f"  inputs: [repository path, objective, constraints]\n"
          f"  outputs: [run report, run manifest]\n"
          f"  risk_level: medium\n  lifecycle: [discover, plan, implement, verify, evidence]\n"
          f"  artifact_types: [report, manifest]\n  related_skills: []\n")
    body = (f"---\n{fm}---\n\n# Axiom {title}\n\n## Purpose\n{title} workflow for {domain}.\n\n"
            "## When to Use\n- Concrete trigger conditions recorded per engagement.\n\n"
            "## When Not to Use\n- As certification proof.\n\n"
            "## Required Inputs\n- Repository path, target files, objective, constraints.\n\n"
            "## Optional Inputs\n- Prior reports and manifests.\n\n"
            "## Prerequisites\n- Base skills loaded.\n\n"
            "## Execution Workflow\n1. Normalize request. 2. Inspect context. 3. Select method. "
            "4. Generate (dry-run first). 5. Validate. 6. Trace. 7. Summarize.\n\n"
            "## Tool Invocations\n- run_skill dry-run first; validate_skill gates release.\n\n"
            "## Decision Rules\n- Flag assumptions; require human review for safety/security output.\n\n"
            "## Workflow\nAs Execution Workflow above.\n\n"
            "## Deliverables\n- Run report + manifest under .axiom/runs/.\n\n"
            "## Acceptance Criteria\n- Checklist green, traceability complete.\n\n"
            "## Acceptance\n- Same gates, machine-checkable.\n\n"
            "## Validation Procedure\n- validate_skills + checklist + human gate.\n\n"
            "## Common Failure Modes\n- Missing inputs invented -> require explicit inputs.\n\n"
            "## Guardrails\n- No secrets/shell/net; never claim compliance.\n\n"
            "## References\n- Standard identifiers + landing URLs only.\n")
    plan = [f"skills/{skill_id}/SKILL.md",
            f"skills/{skill_id}/manifest.yaml",
            f"skills/{skill_id}/checklists/review.yaml"]
    if apply:
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(body, encoding="utf-8")
        (d / "manifest.yaml").write_text(
            f"id: {skill_id}\nversion: 1.2.0\ncontract_version: 1\n"
            f"type: reusable-skill\n"
            f"facets:\n  domains:\n  - {domain}\n  platforms:\n  - mcu\n"
            f"  lifecycle: [discover, plan, implement, verify, evidence]\n"
            f"  artifact_types: [report, manifest]\n"
            f"  risk_level: medium\n  review_required: true\n",
            encoding="utf-8")
        ck = d / "checklists" / "review.yaml"
        ck.parent.mkdir(exist_ok=True)
        ck.write_text("gates:\n  - id: scope\n    text: Scope recorded\n  - id: validate\n    text: Validation green\n",
                      encoding="utf-8")
        for sub in ("references", "templates", "scripts", "tests"):
            (d / sub).mkdir(exist_ok=True)
        # auto-register in catalog.yaml
        cp = ROOT / "skills" / "catalog.yaml"
        if cp.exists():
            cat = yaml.safe_load(cp.read_text(encoding="utf-8")) or {}
            skills = cat.setdefault("skills", [])
            if not any(e.get("id") == skill_id for e in skills):
                skills.append(_catalog_entry(skill_id, title, domain))
                cp.write_text(yaml.safe_dump(cat, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return plan


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--domain", default="automotive")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    try:
        plan = scaffold(args.id, args.title, args.domain, args.apply)
    except (ValueError, FileExistsError) as exc:
        print(f"create_skill: FAIL ({exc})")
        return 1
    print("create_skill: " + ("APPLIED" if args.apply else "DRY-RUN"))
    for p in plan:
        print(f"- {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())