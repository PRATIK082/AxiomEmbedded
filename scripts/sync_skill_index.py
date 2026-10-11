"""Extend registries/skill-index.json + skills.json with axiom-* skills (idempotent)."""
from __future__ import annotations
import json
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    idx_p = ROOT / "registries" / "skill-index.json"
    idx = json.loads(idx_p.read_text(encoding="utf-8"))
    sj_p = ROOT / "registries" / "skills.json"
    sj = json.loads(sj_p.read_text(encoding="utf-8"))
    have = {e["id"] for e in sj["skills"]}
    for e in cat["skills"]:
        fm = yaml.safe_load(
            (ROOT / e["path"] / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1])
        entry = {"description": str(fm.get("description", ""))[:300],
                 "domains": fm.get("domains", []),
                 "platforms": fm.get("platforms", [])}
        idx["skills"][e["id"]] = entry
        if e["id"] not in have:
            sj["skills"].append({"id": e["id"], "path": e["path"]})
    # rebuild facets
    by_d: dict[str, list] = {}
    by_p: dict[str, list] = {}
    for sid, f in idx["skills"].items():
        for d in f.get("domains", []):
            by_d.setdefault(d, []).append(sid)
        for p in f.get("platforms", []):
            by_p.setdefault(p, []).append(sid)
    idx["by_domain"] = {k: sorted(v) for k, v in sorted(by_d.items())}
    idx["by_platform"] = {k: sorted(v) for k, v in sorted(by_p.items())}
    from packages.skills.groups import group_members, validate_groups
    uncovered = validate_groups(cat)
    if uncovered:
        raise SystemExit("skills/groups.yaml covers no group for: " + ", ".join(uncovered))
    idx["by_group"] = {k: v for k, v in sorted(group_members(cat).items())}
    sj["skills"].sort(key=lambda e: e["id"])
    idx_p.write_text(json.dumps(idx, indent=2) + "\n", encoding="utf-8")
    sj_p.write_text(json.dumps(sj, indent=2) + "\n", encoding="utf-8")
    print(f"index: {len(idx['skills'])} skills (+{len(cat['skills'])} axiom-*)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
