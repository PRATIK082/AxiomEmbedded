"""Link pass: derive related/extends/sub_skills/overlays from skills/links.yaml.

Single source: skills/links.yaml (user-editable). Catalog entries for
map-covered skills are overwritten (authoritative); all other skills and
all custom fields are left untouched. No skill is created, renamed, or
duplicated. Rerunnable/idempotent; verifies both link ends exist on disk.

Usage:
  python scripts/link_related_skills.py [--check]
  python scripts/link_related_skills.py --set related <id> <rel>...
  python scripts/link_related_skills.py --set extends <id> <base>
  python scripts/link_related_skills.py --set sub-skills <id> <sub>...
"""
from __future__ import annotations
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINKS = ROOT / "skills" / "links.yaml"

# Bootstrap map (written to links.yaml on first run; edit the YAML after).
BOOTSTRAP_RELATED: dict[str, list[str]] = {
    "autosar": ["axiom-autosar-classic-architecture",
                "axiom-autosar-classic-bsw-integration",
                "axiom-autosar-rte-design", "axiom-autosar-os-config",
                "axiom-autosar-com-stack", "axiom-autosar-adaptive-deployment"],
    "automotive-diagnostics": ["axiom-diagnostics-uds", "axiom-diagnostics-doip"],
    "automotive-networks": ["axiom-can-network-design",
                            "axiom-can-stack-integration",
                            "axiom-automotive-ethernet-someip"],
    "automotive-cybersecurity": ["axiom-vehicle-cybersecurity"],
    "security": ["axiom-vehicle-cybersecurity"],
    "safety": ["axiom-functional-safety"],
    "adas": ["axiom-adas-perception-pipeline", "axiom-adas-validation"],
    "automotive-ota": ["axiom-automotive-release-readiness",
                       "axiom-zonal-architecture"],
    "automotive-middleware": ["axiom-zonal-architecture",
                              "axiom-autosar-adaptive-deployment"],
    "automotive-spice": ["axiom-automotive-release-readiness",
                         "axiom-test-automation"],
    "automotive-vcycle": ["axiom-test-automation", "axiom-hil-test-planning"],
    "automotive-body": ["axiom-can-network-design"],
    "rtos": ["axiom-rtos-architecture"],
    "mcu": ["axiom-embedded-firmware-bringup"],
    "hardware-bringup": ["axiom-embedded-firmware-bringup"],
    "bootloader": ["axiom-embedded-firmware-bringup"],
    "drivers": ["axiom-embedded-firmware-bringup"],
    "debugging": ["axiom-trace-analysis"],
    "performance": ["axiom-memory-and-performance-analysis"],
    "test-automation": ["axiom-test-automation"],
    "unit-test": ["axiom-test-automation"],
    "integration-test": ["axiom-test-automation", "axiom-hil-test-planning"],
    "system-test": ["axiom-hil-test-planning"],
    "coverage": ["axiom-test-automation"],
    "simulation": ["axiom-hil-test-planning"],
    "robotics": ["axiom-robotics-system-integration"],
    "architecture": ["axiom-platform-architecture-review"],
    "software-architecture": ["axiom-platform-architecture-review"],
    "code-review": ["axiom-platform-architecture-review"],
    "requirements": ["axiom-platform-architecture-review"],
    "release": ["axiom-automotive-release-readiness"],
    "evidence": ["axiom-automotive-release-readiness"],
    "soc": ["axiom-zonal-architecture"],
    "mpsoc": ["axiom-zonal-architecture"],
}

BOOTSTRAP_EXTENDS: dict[str, str] = {
    "axiom-autosar-classic-architecture": "autosar",
    "axiom-autosar-classic-bsw-integration": "autosar",
    "axiom-autosar-rte-design": "autosar",
    "axiom-autosar-os-config": "autosar",
    "axiom-autosar-com-stack": "autosar",
    "axiom-autosar-adaptive-deployment": "autosar",
    "axiom-diagnostics-uds": "automotive-diagnostics",
    "axiom-diagnostics-doip": "automotive-diagnostics",
    "axiom-can-network-design": "automotive-networks",
    "axiom-can-stack-integration": "automotive-networks",
    "axiom-automotive-ethernet-someip": "automotive-networks",
    "axiom-vehicle-cybersecurity": "automotive-cybersecurity",
    "axiom-functional-safety": "safety",
    "axiom-adas-perception-pipeline": "adas",
    "axiom-adas-validation": "adas",
    "axiom-automotive-release-readiness": "release",
    "axiom-zonal-architecture": "automotive-middleware",
    "axiom-embedded-firmware-bringup": "hardware-bringup",
    "axiom-rtos-architecture": "rtos",
    "axiom-trace-analysis": "debugging",
    "axiom-memory-and-performance-analysis": "performance",
    "axiom-test-automation": "test-automation",
    "axiom-hil-test-planning": "integration-test",
    "axiom-robotics-system-integration": "robotics",
    "axiom-platform-architecture-review": "architecture",
}

BOOTSTRAP_OVERLAYS: dict[str, list[str]] = {
    "axiom-robotics-system-integration": ["robotics"],
    "axiom-industrial-control-review": ["industrial"],
    "axiom-aerospace-defense-safety-review": ["aerospace", "defense"],
}


def load_links() -> dict:
    if not LINKS.exists():
        LINKS.write_text(yaml.safe_dump({
            "schema_version": "1.0",
            "related": BOOTSTRAP_RELATED,
            "extends": BOOTSTRAP_EXTENDS,
            "domain_overlays": BOOTSTRAP_OVERLAYS,
        }, sort_keys=False), encoding="utf-8")
    return yaml.safe_load(LINKS.read_text(encoding="utf-8"))


def _exists(sid: str) -> bool:
    return (ROOT / "skills" / sid / "SKILL.md").exists()


def derive(maps: dict) -> tuple[dict, dict, dict, int]:
    """Return (related, sub_skills, extends, skipped) derived from maps."""
    related: dict[str, set[str]] = {}
    subs: dict[str, set[str]] = {}
    extends: dict[str, str] = {}
    skipped = 0
    rel = maps.get("related", {}) or {}
    for base, children in rel.items():
        if not _exists(base):
            skipped += len(children or [])
            continue
        for c in children or []:
            if not _exists(c):
                skipped += 1
                continue
            subs.setdefault(base, set()).add(c)
            related.setdefault(base, set()).add(c)
            related.setdefault(c, set()).add(base)
    for child, base in (maps.get("extends", {}) or {}).items():
        if _exists(child) and _exists(base):
            extends[child] = base
            related.setdefault(child, set()).add(base)
            related.setdefault(base, set()).add(child)
        else:
            skipped += 1
    # siblings share a base: children of the same base see each other
    for base, children in subs.items():
        kids = sorted(children)
        for i, a in enumerate(kids):
            for b in kids[i + 1:]:
                related.setdefault(a, set()).add(b)
                related.setdefault(b, set()).add(a)
    return ({k: sorted(v) for k, v in related.items()},
            {k: sorted(v) for k, v in subs.items()}, extends, skipped)


def apply() -> dict:
    maps = load_links()
    related, subs, extends, skipped = derive(maps)
    covered = set(related) | set(subs) | set(extends)
    ov = maps.get("domain_overlays", {}) or {}
    cp = ROOT / "skills" / "catalog.yaml"
    cat = yaml.safe_load(cp.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in cat["skills"]}
    for sid in covered:
        if sid not in by_id:
            skipped += 1
            continue
        e = by_id[sid]
        e["related_skills"] = related.get(sid, [])
        if sid in subs:
            e["sub_skills"] = subs[sid]
        if sid in extends:
            e["extends"] = extends[sid]
        elif "extends" in e and sid.startswith("axiom-"):
            del e["extends"]
    for sid, dirs in ov.items():
        if sid in by_id:
            have = sorted(d for d in dirs if (ROOT / "domains" / d).is_dir())
            skipped += len(dirs) - len(have)
            by_id[sid]["domain_overlays"] = have
    cat["skills"].sort(key=lambda e: e["id"])
    cp.write_text(yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")
    return {"linked": sum(len(v) for v in related.values()),
            "skipped": skipped, "total": len(cat["skills"])}


def set_link(kind: str, sid: str, values: list[str]) -> int:
    maps = load_links()
    if kind == "related":
        maps.setdefault("related", {}).setdefault(sid, [])
        maps["related"][sid] = sorted(set(maps["related"][sid]) | set(values))
    elif kind == "extends":
        maps.setdefault("extends", {})[sid] = values[0]
    elif kind == "sub-skills":
        maps.setdefault("related", {}).setdefault(sid, [])
        maps["related"][sid] = sorted(set(maps["related"][sid]) | set(values))
    else:
        print(f"unknown kind: {kind} (related|extends|sub-skills)")
        return 2
    LINKS.write_text(yaml.safe_dump(maps, sort_keys=False), encoding="utf-8")
    print(apply())
    print(f"{sid}: {kind} recorded in skills/links.yaml + catalog updated")
    return 0


def check() -> int:
    maps = load_links()
    related, subs, extends, _ = derive(maps)
    cp = ROOT / "skills" / "catalog.yaml"
    by_id = {e["id"]: e for e in yaml.safe_load(
        cp.read_text(encoding="utf-8"))["skills"]}
    errors = []
    for sid, want in related.items():
        if sid in by_id and by_id[sid].get("related_skills", []) != want:
            errors.append(f"{sid}: related drift")
    for sid, want in subs.items():
        if sid in by_id and by_id[sid].get("sub_skills", []) != want:
            errors.append(f"{sid}: sub_skills drift")
    for sid, want in extends.items():
        if sid in by_id and by_id[sid].get("extends") != want:
            errors.append(f"{sid}: extends drift")
    if errors:
        print("LINK DRIFT:")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"links OK ({len(related)} related sets, {len(extends)} extends)")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(check())
    if "--set" in sys.argv:
        i = sys.argv.index("--set")
        raise SystemExit(set_link(sys.argv[i + 1], sys.argv[i + 2],
                                  sys.argv[i + 3:]))
    print(apply())
