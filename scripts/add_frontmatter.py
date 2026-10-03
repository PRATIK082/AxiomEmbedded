"""Feature update: skill packaging v1.2.0.

- Injects agent-skills frontmatter (name/description/version/domains/platforms)
  into every skills/<id>/SKILL.md for Claude Code, OpenCode, Codex, Antigravity discovery.
- Bumps each manifest to 1.2.0 with a changelog entry.
- Generates registries/skill-index.json: forward + reverse (domain->skills,
  platform->skills) linkage used by `axiom engage`.

Usage: python scripts/add_frontmatter.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FACETS = REPO_ROOT / "registries" / "skill-facets.yaml"
SKILLS_DIR = REPO_ROOT / "skills"
INDEX = REPO_ROOT / "registries" / "skill-index.json"
NEW_VERSION = "1.2.0"
CHANGELOG_ENTRY = {
    "version": NEW_VERSION,
    "date": "2026-10-03",
    "summary": "Skill packaging: agent-skills frontmatter for multi-harness discovery, domain/platform facets, engagement linkage",
}


def frontmatter(skill_id: str, facet: dict) -> str:
    lines = [
        "---",
        f"name: {skill_id}",
        f"description: {facet['description']}",
        f"version: {NEW_VERSION}",
        f"domains: [{', '.join(facet['domains'])}]",
        f"platforms: [{', '.join(facet['platforms'])}]",
        "---",
    ]
    return "\n".join(lines) + "\n\n"


def main() -> int:
    facets = yaml.safe_load(FACETS.read_text(encoding="utf-8"))["skills"]
    updated = 0
    for skill_id, facet in sorted(facets.items()):
        skill_md = SKILLS_DIR / skill_id / "SKILL.md"
        if not skill_md.exists():
            print(f"SKIP {skill_id}: no SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            # Strip existing frontmatter, re-inject fresh.
            _, _, rest = text.split("---\n", 2)
            text = rest.lstrip("\n")
        skill_md.write_text(frontmatter(skill_id, facet) + text, encoding="utf-8")

        manifest_path = SKILLS_DIR / skill_id / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = NEW_VERSION
        manifest.setdefault("facets", {})["domains"] = facet["domains"]
        manifest["facets"]["platforms"] = facet["platforms"]
        log = manifest.setdefault("changelog", [])
        if not any(e.get("version") == NEW_VERSION for e in log):
            log.append(CHANGELOG_ENTRY)
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        updated += 1

    by_domain: dict[str, list[str]] = {}
    by_platform: dict[str, list[str]] = {}
    for skill_id, facet in sorted(facets.items()):
        for d in facet["domains"]:
            by_domain.setdefault(d, []).append(skill_id)
        for p in facet["platforms"]:
            by_platform.setdefault(p, []).append(skill_id)
    INDEX.write_text(
        json.dumps(
            {"version": "1.0.0", "skills": facets, "by_domain": by_domain, "by_platform": by_platform},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Updated {updated} skills -> v{NEW_VERSION}; index written to {INDEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
