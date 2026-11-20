"""Scaffold missing agents from a template.

Usage: python scripts/scaffold_agents.py --apply
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS = ROOT / "agents"

AGENTS_TO_CREATE = [
    ("skill-evaluation", "Evaluates skill quality, coverage, and maturity across the catalog.",
     "skill-creator", "skill-evaluation"),
    ("skill-adoption", "Adopts and imports external skills into the Axiom catalog with provenance.",
     "skill-seekers", "skill-adoption"),
    ("documentation-generation", "Generates and maintains project documentation from artifacts.",
     "documentation", "documentation-generation"),
    ("cloud-infra", "Cloud and infrastructure engineering for connected embedded products.",
     "terraform-infra", "cloud-infra"),
    ("data-ml", "Data pipelines and ML for edge AI and telemetry.",
     "data-pipeline", "data-ml"),
]

AGENT_MD_TEMPLATE = """# {id} agent

Purpose: {purpose}

## Operating contract

- Use the artifact graph before broad repository reads.
- Load only the profile, workflow, rules and evidence relevant to the task.
- Emit structured findings and evidence references.
- Preserve declared scope; do not silently modify unrelated artifacts.
- Required access class: `read`.
- Writes enabled: `true`.

## Domain-aware execution (Step 0 -- mandatory, agent-specific)
Core skill for THIS agent: `{core_skill}`. Resolve context with `packages/agents/project_context.py::resolve_project_context(repo, prompt, agent_id="{id}")` (explicit axiom.project.yaml > repo signals + prompt keywords > fallback).
Trigger rule (project AND prompt): load project-domain slice, then UNION prompt-domain priority extras (dedup, core first) -- see trigger table. If `needs_clarification` is true (fallback or repo/prompt conflict), ASK the user the `clarification_question` at runtime and wait -- never guess silently.
Token efficiency: open at most 8 SKILL.md files up front (load_plan.primary); consult load_plan.deferred only on demand. Never bulk-load.
Production output: end every run with verdict block [verdict, domain_used, skills_loaded, skills_deferred, standards_applied, evidence_refs, approval_gate, followups] including domain_used, skills_loaded/deferred, standards_applied, evidence_refs and approval_gate. Standards are metadata identifiers only, never compliance claims.
### Trigger table for {id} (core + top domain overlays)
- core: `{core_skill}`
- automotive: axiom-functional-safety, axiom-vehicle-cybersecurity, axiom-diagnostics-uds
- defense: axiom-aerospace-defense-safety-review, safety, security
- aerospace: axiom-aerospace-defense-safety-review, safety, security
- industrial: axiom-industrial-control-review, safety, security
- robotics: axiom-robotics-system-integration, safety, code-review
- energy: axiom-bms-design, axiom-bms-diagnostics, safety
- iot: security, embedded-linux, code-review
- generic-embedded: code-review, static-analysis, implementation
Full map: registries/agent-domain-matrix.json (agent={id}). Guide: docs/agents/domain-aware-execution.md.
"""

MANIFEST_TEMPLATE = {
    "id": None,
    "version": "1.0.0",
    "contract_version": 1,
    "type": "task-agent",
    "writes_enabled": True,
    "access_class": "read",
    "domain_aware": True,
    "requires_project_context": True,
    "skill_binding": {
        "core_skill": None,
        "overlay_source": "configs/domain-routing.yaml",
        "resolver": "packages/agents/project_context.py",
        "matrix": None,
        "token_budget": {"primary_cap": 8, "group_cap": 12, "max_context_files": 8},
        "clarify_when": "needs_clarification=true (fallback or repo/prompt conflict)",
    },
    "output_contract": ["verdict", "domain_used", "skills_loaded", "skills_deferred",
                        "standards_applied", "evidence_refs", "approval_gate", "followups"],
}


def scaffold(apply: bool = False) -> list[str]:
    created = []
    for aid, purpose, core_skill, matrix_key in AGENTS_TO_CREATE:
        d = AGENTS / aid
        if d.exists():
            continue
        created.append(aid)
        if apply:
            d.mkdir(parents=True, exist_ok=True)
            (d / "AGENT.md").write_text(
                AGENT_MD_TEMPLATE.format(id=aid, purpose=purpose, core_skill=core_skill),
                encoding="utf-8")
            m = dict(MANIFEST_TEMPLATE)
            m["id"] = aid
            m["skill_binding"]["core_skill"] = core_skill
            m["skill_binding"]["matrix"] = f"matrix[{aid}]"
            (d / "manifest.json").write_text(json.dumps(m, indent=2), encoding="utf-8")
    return created


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    created = scaffold(args.apply)
    print(f"{'APPLIED' if args.apply else 'DRY-RUN'}: {len(created)} agents")
    for c in created:
        print(f"  - {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
