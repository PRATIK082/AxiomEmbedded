"""Packaging contract: frontmatter, facets, and linkage (ADR-0004)."""

from pathlib import Path
import json

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FRONTMATTER = {"name", "description", "version", "domains", "platforms"}


def _skill_ids():
    return sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())


def test_every_skill_has_complete_frontmatter():
    for sid in _skill_ids():
        text = (ROOT / "skills" / sid / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n"), sid
        _, fm_text, _ = text.split("---\n", 2)
        fm = yaml.safe_load(fm_text)
        assert REQUIRED_FRONTMATTER.issubset(fm), (sid, set(fm))
        assert fm["name"] == sid, sid
        assert len(fm["description"]) >= 20, sid


def test_manifests_carry_facets_and_v120():
    for sid in _skill_ids():
        m = yaml.safe_load((ROOT / "skills" / sid / "manifest.yaml").read_text(encoding="utf-8"))
        assert m["version"] == "1.2.0", sid
        assert "domains" in m.get("facets", {}), sid
        assert "platforms" in m.get("facets", {}), sid


def test_index_linkage_covers_all_skills():
    index = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    assert set(index["skills"]) == set(_skill_ids())
    for domain, skills in index["by_domain"].items():
        for s in skills:
            assert domain in index["skills"][s]["domains"] or "all" in index["skills"][s]["domains"]
    for plat, skills in index["by_platform"].items():
        for s in skills:
            assert plat in index["skills"][s]["platforms"] or "all" in index["skills"][s]["platforms"]


def test_engage_automotive_mcu_is_selective():
    import sys

    sys.path.insert(0, str(ROOT))
    from packages.skills.engage import engage

    sel = engage("automotive", "mcu")
    assert "mcu" in sel["skills"] and "autosar" in sel["skills"]
    assert "robotics" not in sel["skills"]  # robotics is robotics/industrial-only
    assert "embedded-linux" not in sel["skills"]  # mpu/soc only
    assert 0 < sel["skill_count"] < len(_skill_ids())
