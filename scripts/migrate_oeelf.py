from __future__ import annotations
import argparse
from pathlib import Path

MAP = {
    "framework/schemas": "schemas",
    "framework/taxonomy": "taxonomies",
    "domains": "domains",
    "skills": "skills",
    "rulesets": "rules",
    "workflows": "workflows",
    "profiles": "profiles",
    "traceability": "packages/core",
    "technology-packs": "platforms",
    "tool-adapters": "tools",
}

def main() -> int:
    ap = argparse.ArgumentParser(description="Print external AxiomEmbedded →AxiomEmbedded migration mappings")
    ap.add_argument("--source", required=True, help="External AxiomEmbedded  checkout or extracted source directory")
    args = ap.parse_args()
    root = Path(args.source)
    if not root.exists():
        ap.error(f"AxiomEmbedded  source does not exist: {root}")
    for old, new in MAP.items():
        print(f"{root / old} -> {new}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
