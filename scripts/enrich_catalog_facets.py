"""Backfill prompt2 discovery facets into skills/catalog.yaml from SKILL.md axiom: blocks.

SKILL.md frontmatter stays the single source of truth; this script only copies
lifecycle/standards/artifact_types/mcp_tools/risk_level/review_required into the
matching catalog entries (axiom-* skills). Idempotent. Usage:
  python scripts/enrich_catalog_facets.py [--check]
"""
from __future__ import annotations
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
FACETS = ("lifecycle", "standards", "artifact_types", "mcp_tools",
          "risk_level", "review_required")


def load_fm(skill_id: str) -> dict:
    text = (ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1]) or {}


def enrich(check: bool = False) -> int:
    cat_p = ROOT / "skills" / "catalog.yaml"
    cat = yaml.safe_load(cat_p.read_text(encoding="utf-8"))
    drift = []
    for entry in cat["skills"]:
        sid = entry["id"]
        if not sid.startswith("axiom-"):
            continue
        ax = (load_fm(sid).get("axiom") or {})
        for facet in FACETS:
            want = ax.get(facet, [] if facet not in ("risk_level",) else "medium")
            if facet == "risk_level" and want is None:
                want = "medium"
            if entry.get(facet) != want:
                drift.append(f"{sid}.{facet}")
                if not check:
                    entry[facet] = want
    if check:
        if drift:
            print("FACET DRIFT:")
            for d in drift:
                print(f"- {d}")
            return 1
        print(f"facet parity OK: {len(cat['skills'])} entries")
        return 0
    cat_p.write_text(yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")
    print(f"enriched {len(drift)} facet fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(enrich("--check" in sys.argv))
