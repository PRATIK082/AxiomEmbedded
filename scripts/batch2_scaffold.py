"""Batch 2 scaffolding: ensure every skill has tests/, scripts/validate.py, references/, templates/, checklists/.

Stdlib only. Idempotent: skips files that already exist. Run from repo root.
"""
from __future__ import annotations
import json
import os
import pathlib
import yaml

ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded")
SKILLS = ROOT / "skills"

def load_fm(sid):
    p = SKILLS / sid / "SKILL.md"
    txt = p.read_text(encoding="utf-8")
    if not txt.startswith("---"):
        return {}
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        return {}

def scaffold(sid):
    d = SKILLS / sid
    fm = load_fm(sid)
    name = fm.get("name", sid)
    desc = fm.get("description", "")
    domains = fm.get("domains", [])
    domain = domains[0] if domains else "all"
    axiom = fm.get("axiom", {}) if isinstance(fm.get("axiom"), dict) else {}
    maturity = axiom.get("maturity", "experimental")
    standards = axiom.get("standards", []) or []
    artifacts = axiom.get("artifact_types", []) or []
    related = axiom.get("related_skills", []) or []

    # tests/evals.json
    tdir = d / "tests"
    tdir.mkdir(exist_ok=True)
    evals = tdir / "evals.json"
    if not evals.exists():
        scenarios = [
            {
                "id": f"{sid}-E01",
                "title": "Happy path produces the primary artifact",
                "query": f"Apply {name} to a representative input and produce the expected deliverable.",
                "expected_behavior": [
                    "Skill activates on the trigger description",
                    "Required inputs are collected or defaulted",
                    "Primary artifact is produced in the documented format",
                    "Acceptance criteria are evaluated",
                ],
            },
            {
                "id": f"{sid}-E02",
                "title": "Missing required input is flagged",
                "query": f"Invoke {name} without a required input.",
                "expected_behavior": [
                    "Skill reports the missing input",
                    "No partial artifact is written",
                    "Guidance is given to supply the input",
                ],
            },
            {
                "id": f"{sid}-E03",
                "title": "Boundary / out-of-scope request is refused",
                "query": f"Ask {name} to perform a task outside its scope.",
                "expected_behavior": [
                    "Skill identifies out-of-scope condition",
                    "Skill suggests the appropriate related skill if any",
                    "No unsafe action is taken",
                ],
            },
        ]
        evals.write_text(json.dumps({"skill": sid, "version": fm.get("version", "1.0.0"),
                                    "scenarios": scenarios}, indent=2) + "\n", encoding="utf-8")

    # scripts/validate.py
    sdir = d / "scripts"
    sdir.mkdir(exist_ok=True)
    vpy = sdir / "validate.py"
    if not vpy.exists():
        content = '''"""Validation script for %s (stdlib only).

Run: python scripts/validate.py [artifact_dir]
"""
from __future__ import annotations
import json
import pathlib
import sys


def main() -> int:
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    errors = []
    # Skill-specific checks are added during content refinement.
    # Generic structural checks:
    skill_dir = pathlib.Path(__file__).resolve().parents[1]
    if not (skill_dir / "SKILL.md").exists():
        errors.append("SKILL.md missing")
    if not (skill_dir / "manifest.yaml").exists():
        errors.append("manifest.yaml missing")
    if not (skill_dir / "checklists").is_dir():
        errors.append("checklists/ missing")
    # validate evals.json if present
    evals = skill_dir / "tests" / "evals.json"
    if evals.exists():
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
            if not isinstance(data.get("scenarios"), list) or len(data["scenarios"]) < 1:
                errors.append("evals.json must contain >=1 scenario")
        except Exception as exc:
            errors.append(f"evals.json parse error: {exc}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''' % sid
        vpy.write_text(content, encoding="utf-8")

    # references/overview.md
    rdir = d / "references"
    rdir.mkdir(exist_ok=True)
    # create at least one reference file if none
    existing_refs = [p for p in rdir.iterdir() if p.is_file()]
    if not existing_refs:
        (rdir / "overview.md").write_text(
            f"# {name} — References\n\n"
            f"Skill: `{sid}`. Domain: {domain}. Maturity: {maturity}.\n\n"
            f"## Standards (identifiers only)\n"
            + "".join(f"- {s}\n" for s in standards) + ("\n" if standards else "- (none declared)\n")
            + "\n## Artifacts\n"
            + "".join(f"- {a}\n" for a in artifacts) + ("\n" if artifacts else "- (none declared)\n")
            + "\n## Related skills\n"
            + "".join(f"- {r}\n" for r in related) + ("\n" if related else "- (none)\n")
            + "\nNo proprietary normative text is reproduced. See public standard landing pages for normative content.\n",
            encoding="utf-8")

    # templates/
    tdir2 = d / "templates"
    tdir2.mkdir(exist_ok=True)
    existing_tpl = [p for p in tdir2.iterdir() if p.is_file()]
    if not existing_tpl:
        (tdir2 / "artifact.template.md").write_text(
            f"# {name} — artifact template\n\n"
            "## Header\n- skill: " + sid + "\n- version: " + str(fm.get("version","1.0.0")) + "\n- date: <ISO8601>\n\n"
            "## Body\n<fill per skill-specific schema>\n\n"
            "## Evidence\n- checks run:\n- reviewer:\n",
            encoding="utf-8")

    # checklists/
    cdir = d / "checklists"
    cdir.mkdir(exist_ok=True)
    existing_cl = [p for p in cdir.iterdir() if p.is_file()]
    if not existing_cl:
        (cdir / "review.yaml").write_text(
            "# Axiom skill review checklist\n"
            "gates:\n"
            "  - id: scope\n    text: Scope, inputs, and prerequisites recorded\n"
            "  - id: method\n    text: Workflow steps executed in order with evidence\n"
            "  - id: validation\n    text: Schema/lint/consistency checks run and green\n"
            "  - id: traceability\n    text: Requirements-to-artifact links complete\n"
            "  - id: review\n    text: Human review done for safety/security-relevant output\n",
            encoding="utf-8")


def main():
    count = 0
    for p in sorted(SKILLS.iterdir()):
        if not p.is_dir() or p.name.startswith(("_", ".")):
            continue
        if not (p / "SKILL.md").exists():
            continue
        scaffold(p.name)
        count += 1
    print(f"scaffolded {count} skills")


if __name__ == "__main__":
    main()
