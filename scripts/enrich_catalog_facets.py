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
# DESA Phase 2 facets: canonical names stored in catalog.yaml.
DESA_FACETS = ("activity", "capability_kind", "primary_domain",
               "risk_class", "lifecycle_phases", "standard_ids")
# axiom: block aliases accepted for backward compatibility.
DESA_ALIASES = {
    "activity": ("activity",),
    "capability_kind": ("capability_kind", "capability-kind", "type"),
    "primary_domain": ("primary_domain", "domain"),
    "risk_class": ("risk_class", "risk_level"),
    "lifecycle_phases": ("lifecycle_phases", "lifecycle"),
    "standard_ids": ("standard_ids", "standards"),
}


def load_fm(skill_id: str) -> dict:
    text = (ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1]) or {}


def _desa_want(ax: dict, facet: str):
    for alias in DESA_ALIASES.get(facet, (facet,)):
        if alias in ax and ax[alias] is not None:
            val = ax[alias]
            # risk_class defaults to risk_level medium; normalize safety flags.
            if facet == "risk_class" and val == "medium":
                pass
            return val
    if facet in ("activity", "capability_kind"):
        return ""
    if facet in ("lifecycle_phases", "standard_ids"):
        return []
    if facet == "primary_domain":
        return str(ax.get("domain", "generic-embedded"))
    if facet == "risk_class":
        return str(ax.get("risk_level", "medium"))
    return ""


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
        for facet in DESA_FACETS:
            want = _desa_want(ax, facet)
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
