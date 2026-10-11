"""Build the plug-and-play toolpack index (mirrors scripts/add_frontmatter.py).

- Stamps `facets:` (domains/platforms/standards) into every tools/<id>/manifest.yaml
  from registries/tool-facets.yaml (no version bumps).
- Generates registries/tools.json (id -> path) and registries/tool-index.json
  (facets + by_domain/by_platform/by_standard) used by `axiom packs`.

Usage: python scripts/build_tool_index.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FACETS = REPO_ROOT / "registries" / "tool-facets.yaml"
TOOLS_DIR = REPO_ROOT / "tools"
REGISTRY = REPO_ROOT / "registries" / "tools.json"
INDEX = REPO_ROOT / "registries" / "tool-index.json"


def main() -> int:
    facets = yaml.safe_load(FACETS.read_text(encoding="utf-8"))["tools"]
    stamped = 0
    for tool_id, facet in sorted(facets.items()):
        manifest_path = TOOLS_DIR / tool_id / "manifest.yaml"
        if not manifest_path.exists():
            print(f"SKIP {tool_id}: no manifest.yaml")
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        manifest.setdefault("facets", {})["domains"] = facet["domains"]
        manifest["facets"]["platforms"] = facet["platforms"]
        manifest["facets"]["standards"] = facet.get("standards", [])
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        stamped += 1

    by_domain: dict[str, list[str]] = {}
    by_platform: dict[str, list[str]] = {}
    by_standard: dict[str, list[str]] = {}
    for tool_id, facet in sorted(facets.items()):
        for d in facet["domains"]:
            by_domain.setdefault(d, []).append(tool_id)
        for p in facet["platforms"]:
            by_platform.setdefault(p, []).append(tool_id)
        for s in facet.get("standards", []):
            by_standard.setdefault(s, []).append(tool_id)
    REGISTRY.write_text(
        json.dumps(
            {"schema_version": "1.0",
             "tools": [{"id": t, "path": f"tools/{t}"} for t in sorted(facets)]},
            indent=2,
        ),
        encoding="utf-8",
    )
    INDEX.write_text(
        json.dumps(
            {"version": "1.0.0", "tools": facets,
             "by_domain": by_domain, "by_platform": by_platform, "by_standard": by_standard},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Stamped {stamped} tools; registry + index written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
