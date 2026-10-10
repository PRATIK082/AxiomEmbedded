"""Compose a skill mind-map DAG from a user prompt + facet axes.

Pipeline (all deterministic, stdlib-only):
  prompt -> detect domain/intent -> engage skills -> select toolpacks ->
  stage-chain filter -> DAG nodes/edges + traceability chains + mermaid.

The composer never invents skills or tools: every node comes from the live
`engage` / `select_packs` slices. All seven axes (domain, platform, os,
language, standards, hardware, technology) are carried in the output schema
so future indexes can score them; v1 scores domain/platform/standards.

Stage order follows the V-model right arm used by workflows/feature-change.yaml:
requirements -> architecture -> implementation -> tests -> review ->
traceability -> evidence.
"""

from __future__ import annotations

# Canonical stage order with the skill ids that can serve each stage.
# A stage enters the chain only if at least one of its skills is engaged.
STAGES: list[tuple[str, list[str]]] = [
    ("requirements", ["requirements"]),
    ("architecture", ["software-architecture", "architecture", "hardware-architecture"]),
    ("implementation", ["implementation", "embedded-c", "embedded-cpp", "rust-embedded",
                        "autosar", "automotive-diagnostics", "mcu", "drivers", "bootloader"]),
    ("tests", ["unit-test", "integration-test", "system-test", "validation",
               "test-automation", "automotive-diagnostics", "coverage", "fault-injection"]),
    ("review", ["code-review", "static-analysis"]),
    ("traceability", ["requirements-traceability", "traceability"]),
    ("evidence", ["evidence"]),
]

# Intent keywords (lowercase substrings) selecting stages from the prompt.
INTENT_STAGES: list[tuple[str, list[str]]] = [
    ("requirement", ["requirements", "traceability"]),
    ("spec", ["requirements"]),
    ("analys", ["requirements"]),
    ("architect", ["architecture"]),
    ("design", ["architecture"]),
    ("code", ["implementation"]),
    ("develop", ["implementation"]),
    ("implement", ["implementation"]),
    ("generat", ["implementation", "tests"]),
    ("script", ["implementation", "tests"]),
    ("test", ["tests"]),
    ("validat", ["tests"]),
    ("verif", ["tests"]),
    ("review", ["review"]),
    ("map", ["traceability"]),
    ("trac", ["traceability"]),
    ("evidence", ["evidence"]),
    ("report", ["evidence"]),
]

# Fixed traceability edges between stages (REQ->CODE, REQ->TEST, ...).
TRACE_EDGES: list[tuple[str, str, str]] = [
    ("requirements", "implementation", "REQ->CODE"),
    ("requirements", "tests", "REQ->TEST"),
    ("implementation", "review", "CODE->REVIEW"),
    ("tests", "evidence", "TEST->EVIDENCE"),
    ("traceability", "evidence", "MAP->EVIDENCE"),
]


def detect_stages(prompt: str) -> list[str]:
    """Stages selected by intent keywords; full chain when nothing matches."""
    lower = (prompt or "").lower()
    wanted: list[str] = []
    for keyword, stages in INTENT_STAGES:
        if keyword in lower:
            wanted.extend(s for s in stages if s not in wanted)
    if not wanted:
        return [name for name, _ in STAGES]
    return [name for name, _ in STAGES if name in wanted]


def compose_mindmap(
    prompt: str,
    domain: str | None = None,
    platform: str | None = None,
    os: str | None = None,
    language: str | None = None,
    standards: list[str] | None = None,
    hardware: str | None = None,
    technology: str | None = None,
) -> dict:
    from packages.agents.router import detect_domain, route
    from packages.skills.engage import engage
    from packages.toolpacks.select import select_packs

    standards = standards or []
    if not domain:
        domain = detect_domain(prompt or "")
    engagement = engage(domain, platform)
    packs = select_packs(domain, platform, standards)
    engaged = set(engagement["skills"])

    chain: list[dict] = []
    seen: set[str] = set()
    for stage, candidates in STAGES:
        skills = [s for s in candidates if s in engaged and s not in seen]
        if not skills:
            continue
        seen.update(skills)
        chain.append({"stage": stage, "skills": skills})

    wanted = detect_stages(prompt)
    chain = [link for link in chain if link["stage"] in wanted]

    present = {link["stage"] for link in chain}
    edges = [{"from": a, "to": b, "via": label} for a, b, label in TRACE_EDGES
             if a in present and b in present]
    for prev, nxt in zip(chain, chain[1:]):
        if not any(e["from"] == prev["stage"] and e["to"] == nxt["stage"] for e in edges):
            edges.append({"from": prev["stage"], "to": nxt["stage"], "via": "FLOW"})

    trace_chains = [
        {"id": "REQ-CODE", "from": "requirements/SYS-xxx", "to": "src/<handler>",
         "via": "implementation skills", "record": "traceability-matrix"},
        {"id": "REQ-TEST", "from": "requirements/SYS-xxx", "to": "test/<case>",
         "via": "test skills + generated vectors", "record": "uds_traceability.csv"},
    ]
    return {
        "prompt": prompt,
        "axes": {"domain": domain, "platform": platform, "os": os, "language": language,
                 "standards": standards, "hardware": hardware, "technology": technology},
        "intent": route(prompt or ""),
        "stages": [link["stage"] for link in chain],
        "chain": chain,
        "edges": edges,
        "trace_chains": trace_chains,
        "tools": packs["tools"],
        "install": packs["install"],
        "agents": packs["agents"],
        "orchestrator": "skill-orchestrator",
        "mermaid": render_mermaid(chain, edges),
        "approval_required_for": ["git push", "release", "destructive_command",
                                  "safety_critical_change", "security_critical_change"],
    }


def render_mermaid(chain: list[dict], edges: list[dict]) -> str:
    """Mermaid flowchart of the skill mind-map (derived view, not source of truth)."""
    lines = ["flowchart LR"]
    for link in chain:
        skills = "\\n".join(link["skills"])
        lines.append(f'    {link["stage"]}["{link["stage"]}\\n{skills}"]')
    for i, prev in enumerate(chain):
        for nxt in chain[i + 1:]:
            edge = next((e for e in edges if e["from"] == prev["stage"] and e["to"] == nxt["stage"]), None)
            if edge:
                lines.append(f'    {prev["stage"]} -->|{edge["via"]}| {nxt["stage"]}')
                break
    for edge in edges:
        if edge["via"] in ("REQ->CODE", "REQ->TEST"):
            lines.append(f'    {edge["from"]} -.->|{edge["via"]}| {edge["to"]}')
    return "\n".join(lines)
