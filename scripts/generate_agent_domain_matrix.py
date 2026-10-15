#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate registries/agent-domain-matrix.json from single sources.

Sources (hand-edited only):
  agents/*/manifest.json + AGENT.md
  configs/domain-routing.yaml (domain -> profile/platforms/standards/groups/priority_skills)
  registries/skill-index.json (skill facets + by_group views)

Output (generated, do not edit by hand):
  registries/agent-domain-matrix.json — agent x domain -> skills/platforms/standards/profiles

Usage:
  python scripts/generate_agent_domain_matrix.py        # regenerate in place
  python scripts/generate_agent_domain_matrix.py --check # CI: exit 1 if stale
"""
from __future__ import annotations

import argparse
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_matrix() -> dict:
    routing = yaml.safe_load((ROOT / "configs" / "domain-routing.yaml").read_text(encoding="utf-8"))
    index = json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    by_group = index.get("by_group", {})
    core_by_agent = (routing.get("agent_binding", {}) or {}).get("core_skill_by_agent", {})
    agent_ids = sorted(p.parent.name for p in (ROOT / "agents").glob("*/manifest.json"))
    matrix: dict[str, dict] = {}
    for agent in agent_ids:
        matrix[agent] = {}
        core = core_by_agent.get(agent)
        for domain, spec in (routing.get("domains") or {}).items():
            groups = spec.get("skill_groups", [])
            group_skills: list[str] = []
            for group in groups:
                group_skills.extend(by_group.get(group, []))
            priority = [s for s in spec.get("priority_skills", []) if s in index.get("skills", {})]
            skills: list[str] = []
            for candidate in ([core] if core else []) + priority + sorted(set(group_skills)):
                if candidate and candidate in index.get("skills", {}) and candidate not in skills:
                    skills.append(candidate)
            matrix[agent][domain] = {
                "core_skill": core,
                "skills": skills,
                "skill_count": len(skills),
                "platforms": spec.get("platforms", []),
                "standards": spec.get("standards", []),
                "profiles": [spec.get("default_profile")],
                "notes": ("defense reuses shared axiom-aerospace-defense-safety-review; no defense-only duplicate by design."
                          if domain in ("defense", "aerospace") else ""),
            }
    return {"schema_version": "1.0",
            "sources": ["configs/domain-routing.yaml", "registries/skill-index.json", "agents/*/manifest.json"],
            "defaults": routing.get("defaults", {}),
            "runtime": routing.get("runtime", {}),
            "matrix": matrix}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    out_path = ROOT / "registries" / "agent-domain-matrix.json"
    data = build_matrix()
    text = json.dumps(data, indent=2) + "\n"
    if args.check:
        current = out_path.read_text(encoding="utf-8") if out_path.exists() else None
        if current != text:
            print("Stale registries/agent-domain-matrix.json (run python scripts/generate_agent_domain_matrix.py)")
            return 1
        print("agent-domain-matrix up to date.")
        return 0
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path} ({len(data['matrix'])} agents x {len(next(iter(data['matrix'].values())))} domains)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
