"""Scaffold the 30 axiom-* skills + catalog.yaml + registry.yaml (deterministic, rerunnable).

Usage: python scripts/scaffold_axiom_skills.py [--check]
--check verifies every expected file exists without writing.
Original content throughout; no reference-repo text used.
"""
from __future__ import annotations
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

# id, title, domain, subdomain, category, maturity, description, platforms, standards, artifacts, risk
SKILLS: list[dict] = [
 {"id": "axiom-autosar-classic-architecture", "title": "AUTOSAR Classic Architecture Review", "domain": "automotive", "subdomain": "autosar-classic", "category": "architecture", "maturity": "beta", "desc": "Reviews AUTOSAR Classic platform architecture choices, layering, and release baselines for an ECU project and produces an architecture decision record with findings.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11", "ISO 26262:2018"], "artifacts": ["architecture decision record", "layering review"], "risk": "high"},
 {"id": "axiom-autosar-classic-bsw-integration", "title": "AUTOSAR Classic BSW Integration", "domain": "automotive", "subdomain": "autosar-classic", "category": "integration", "maturity": "beta", "desc": "Integrates and reviews AUTOSAR Classic BSW configuration (ARXML/BMD/RTE/OS/COM/PduR/CanIf/CanTp/Dcm/Dem/NvM/EcuM) and produces an integration report with severity-ranked findings and a validation matrix.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11", "ISO 26262:2018"], "artifacts": ["integration report", "validation matrix", "configuration-change plan"], "risk": "high"},
 {"id": "axiom-autosar-rte-design", "title": "AUTOSAR RTE Design", "domain": "automotive", "subdomain": "autosar-classic", "category": "design", "maturity": "experimental", "desc": "Designs RTE ports, interfaces, runnable entities and events for Classic software components with consistency checks and traceability.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11"], "artifacts": ["RTE mapping table", "interface contract"], "risk": "medium"},
 {"id": "axiom-autosar-os-config", "title": "AUTOSAR OS Configuration Review", "domain": "automotive", "subdomain": "autosar-classic", "category": "configuration", "maturity": "experimental", "desc": "Reviews AUTOSAR OS task, alarm, schedule-table and timing-protection configuration against scheduling constraints and stack assumptions.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11"], "artifacts": ["OS config review", "scheduling analysis"], "risk": "high"},
 {"id": "axiom-autosar-com-stack", "title": "AUTOSAR COM Stack Review", "domain": "automotive", "subdomain": "autosar-classic", "category": "configuration", "maturity": "experimental", "desc": "Reviews COM/PduR/CanIf/CanTp signal routing, PDU mapping and gateway assumptions for Classic communication stacks.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11"], "artifacts": ["COM review", "signal-routing table"], "risk": "medium"},
 {"id": "axiom-autosar-adaptive-deployment", "title": "AUTOSAR Adaptive Deployment", "domain": "automotive", "subdomain": "autosar-adaptive", "category": "deployment", "maturity": "experimental", "desc": "Designs Adaptive service deployment (ara::com manifests, execution/state management, persistency, time sync) with a deployment checklist.", "platforms": ["mpu", "autosar-adaptive"], "standards": ["AUTOSAR Adaptive R24-11"], "artifacts": ["deployment manifest review", "deployment checklist"], "risk": "high"},
 {"id": "axiom-can-network-design", "title": "CAN Network Design", "domain": "automotive", "subdomain": "networks", "category": "design", "maturity": "beta", "desc": "Designs CAN/CAN-FD network topology, identifier allocation, bus-load budgets and timing assumptions from DBC-level inputs.", "platforms": ["mcu", "autosar-classic"], "standards": ["ISO 11898"], "artifacts": ["network design", "bus-load budget"], "risk": "medium"},
 {"id": "axiom-can-stack-integration", "title": "CAN Stack Integration", "domain": "automotive", "subdomain": "networks", "category": "integration", "maturity": "experimental", "desc": "Integrates and checks CAN driver/CanIf/CanTp stacks including baud-rate, mailbox, and error-handling configuration.", "platforms": ["mcu", "autosar-classic"], "standards": ["ISO 11898"], "artifacts": ["stack integration report"], "risk": "medium"},
 {"id": "axiom-automotive-ethernet-someip", "title": "Automotive Ethernet and SOME/IP Design", "domain": "automotive", "subdomain": "networks", "category": "design", "maturity": "experimental", "desc": "Designs Ethernet topology, VLAN/TSN assumptions and SOME/IP service modeling for service-oriented ECUs.", "platforms": ["mpu", "autosar-adaptive"], "standards": ["AUTOSAR SOME/IP", "IEEE 802.1 TSN"], "artifacts": ["Ethernet design", "service model"], "risk": "medium"},
 {"id": "axiom-diagnostics-uds", "title": "UDS Diagnostics Design and Validation", "domain": "automotive", "subdomain": "diagnostics", "category": "verification", "maturity": "beta", "desc": "Designs UDS service coverage, session/security posture and negative-response matrices, and validates them with a deterministic checker script.", "platforms": ["mcu", "mpu", "autosar-classic", "autosar-adaptive"], "standards": ["ISO 14229-1", "ISO 26262:2018"], "artifacts": ["diagnostic requirements", "service matrix", "validation report"], "risk": "high"},
 {"id": "axiom-diagnostics-doip", "title": "DoIP Diagnostics Integration", "domain": "automotive", "subdomain": "diagnostics", "category": "integration", "maturity": "experimental", "desc": "Integrates DoIP discovery, routing activation and diagnostic transport for Ethernet ECUs with tester-workflow checks.", "platforms": ["mpu", "autosar-adaptive"], "standards": ["ISO 13400-2"], "artifacts": ["DoIP integration review"], "risk": "medium"},
 {"id": "axiom-vehicle-cybersecurity", "title": "Vehicle Cybersecurity Workflow", "domain": "automotive", "subdomain": "cybersecurity", "category": "security", "maturity": "experimental", "desc": "Runs a TARA-aligned cybersecurity workflow (threat model, secure boot/diag, key management, IDS/OTA concepts) producing reviewable evidence.", "platforms": ["mcu", "mpu"], "standards": ["ISO/SAE 21434"], "artifacts": ["threat model", "security review"], "risk": "safety-critical"},
 {"id": "axiom-functional-safety", "title": "Functional Safety Workflow", "domain": "automotive", "subdomain": "safety", "category": "safety", "maturity": "experimental", "desc": "Supports HARA, safety goals, FSR/TSR derivation, FMEA/FTA templates and verification-evidence structure for safety-related work.", "platforms": ["mcu", "mpu"], "standards": ["ISO 26262:2018"], "artifacts": ["safety plan", "FMEA/FTA templates", "evidence structure"], "risk": "safety-critical"},
 {"id": "axiom-adas-perception-pipeline", "title": "ADAS Perception Pipeline Design", "domain": "automotive", "subdomain": "adas", "category": "design", "maturity": "experimental", "desc": "Designs sensor-abstraction, perception interfaces and object-model contracts for ADAS pipelines.", "platforms": ["mpu", "soc"], "standards": ["ISO 26262:2018"], "artifacts": ["perception interface contract"], "risk": "high"},
 {"id": "axiom-adas-validation", "title": "ADAS Validation Planning", "domain": "automotive", "subdomain": "adas", "category": "verification", "maturity": "experimental", "desc": "Plans sensor-fusion validation, recording/replay campaigns and KPI definitions for ADAS functions.", "platforms": ["mpu", "soc"], "standards": ["ISO 26262:2018"], "artifacts": ["validation plan", "KPI set"], "risk": "high"},
 {"id": "axiom-bms-design", "title": "BMS Control Design", "domain": "automotive", "subdomain": "bms", "category": "design", "maturity": "experimental", "desc": "Designs cell modeling assumptions, SOC/SOH method selection, contactor/precharge, insulation monitoring and thermal strategy for battery systems.", "platforms": ["mcu"], "standards": ["ISO 26262:2018"], "artifacts": ["BMS design review", "fault-handling table"], "risk": "high"},
 {"id": "axiom-bms-diagnostics", "title": "BMS Diagnostics and HIL Test Design", "domain": "automotive", "subdomain": "bms", "category": "verification", "maturity": "experimental", "desc": "Designs BMS fault handling and HIL test campaigns covering cell, contactor, thermal and isolation faults.", "platforms": ["mcu"], "standards": ["ISO 26262:2018"], "artifacts": ["HIL test plan"], "risk": "high"},
 {"id": "axiom-v2x-communication", "title": "V2X Communication Design", "domain": "automotive", "subdomain": "v2x", "category": "design", "maturity": "experimental", "desc": "Models V2X messages, latency/security considerations and simulation hooks with a message test strategy.", "platforms": ["mpu"], "standards": ["ETSI ITS-G5"], "artifacts": ["message model", "test strategy"], "risk": "medium"},
 {"id": "axiom-zonal-architecture", "title": "Zonal Architecture Design", "domain": "automotive", "subdomain": "zonal", "category": "architecture", "maturity": "experimental", "desc": "Designs zonal/domain-controller partitioning, service-oriented communication, compute allocation and update strategy.", "platforms": ["mcu", "mpu", "soc"], "standards": ["AUTOSAR"], "artifacts": ["zonal architecture record"], "risk": "medium"},
 {"id": "axiom-automotive-release-readiness", "title": "Automotive Release Readiness", "domain": "automotive", "subdomain": "release", "category": "release", "maturity": "experimental", "desc": "Gates ECU/software release readiness with evidence packaging, open-finding triage and sign-off checklists.", "platforms": ["mcu", "mpu"], "standards": ["Automotive SPICE"], "artifacts": ["release gate report", "evidence package"], "risk": "high"},
 {"id": "axiom-embedded-firmware-bringup", "title": "Embedded Firmware Bring-up", "domain": "platform", "subdomain": "bringup", "category": "implementation", "maturity": "experimental", "desc": "Brings up firmware on a new MCU/board (clock, memory, drivers, bootloader handoff) with a deterministic checklist.", "platforms": ["mcu", "bare-metal"], "standards": [], "artifacts": ["bring-up checklist", "bring-up report"], "risk": "medium"},
 {"id": "axiom-rtos-architecture", "title": "RTOS Architecture Review", "domain": "platform", "subdomain": "rtos", "category": "architecture", "maturity": "experimental", "desc": "Reviews RTOS task, priority, IPC and timing architecture for determinism and stack safety.", "platforms": ["mcu", "rtos"], "standards": [], "artifacts": ["RTOS review"], "risk": "medium"},
 {"id": "axiom-trace-analysis", "title": "Trace Analysis", "domain": "platform", "subdomain": "observability", "category": "verification", "maturity": "experimental", "desc": "Analyzes execution traces for timing, dropped events and anomaly triage with a deterministic parser script.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["trace analysis report"], "risk": "low"},
 {"id": "axiom-memory-and-performance-analysis", "title": "Memory and Performance Analysis", "domain": "platform", "subdomain": "performance", "category": "verification", "maturity": "experimental", "desc": "Analyzes memory classification, stack/heap budgets and performance hotspots against project budgets.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["memory/perf report"], "risk": "medium"},
 {"id": "axiom-test-automation", "title": "Embedded Test Automation", "domain": "platform", "subdomain": "testing", "category": "verification", "maturity": "experimental", "desc": "Designs unit/integration test strategy, automation hooks and coverage expectations for embedded repos.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["test strategy", "test plan"], "risk": "low"},
 {"id": "axiom-hil-test-planning", "title": "HIL Test Planning", "domain": "platform", "subdomain": "testing", "category": "verification", "maturity": "experimental", "desc": "Plans SIL/HIL campaigns including plant models, fault injection and pass/fail criteria.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["HIL test plan"], "risk": "medium"},
 {"id": "axiom-robotics-system-integration", "title": "Robotics System Integration", "domain": "robotics", "subdomain": "integration", "category": "integration", "maturity": "experimental", "desc": "Integrates ROS 2 nodes, sensor fusion and motion-control interfaces with contract checks.", "platforms": ["mpu", "soc"], "standards": [], "artifacts": ["integration review"], "risk": "medium"},
 {"id": "axiom-industrial-control-review", "title": "Industrial Control Review", "domain": "industrial", "subdomain": "control", "category": "review", "maturity": "experimental", "desc": "Reviews PLC/fieldbus/OPC-UA control designs and functional-safety touchpoints for industrial controllers.", "platforms": ["mcu", "mpu"], "standards": ["IEC 61508"], "artifacts": ["control review"], "risk": "high"},
 {"id": "axiom-aerospace-defense-safety-review", "title": "Aerospace and Defense Safety Review", "domain": "aerospace", "subdomain": "safety", "category": "review", "maturity": "experimental", "desc": "Reviews safety-critical embedded designs against DO-178C/DO-254-style objectives and evidence expectations.", "platforms": ["mcu", "mpu"], "standards": ["DO-178C", "DO-254"], "artifacts": ["safety review"], "risk": "safety-critical"},
 {"id": "axiom-platform-architecture-review", "title": "Platform Architecture Review", "domain": "cross-domain", "subdomain": "architecture", "category": "architecture", "maturity": "experimental", "desc": "Reviews embedded platform architecture (requirements-to-design traceability, interface contracts, ADRs, tech-debt) for any domain.", "platforms": ["mcu", "mpu", "soc"], "standards": [], "artifacts": ["architecture review", "ADR set"], "risk": "medium"},
]

SKILL_MD = """---\n{name}\n---\n\n# Axiom {title}\n\n## Purpose\n{desc}\n\nScope: {subdomain} ({domain}). Maturity: {maturity}. This skill is original AxiomEmbedded content.\n\n## When to Use\n- The project needs the {title_lower} engineering workflow.\n- Inputs listed below are available.\n\n## When Not to Use\n- As a substitute for qualified safety/security certification review.\n- When the required inputs are absent (record the gap instead of inventing data).\n\n## Required Inputs\n- Repository path and target file list.\n- User objective and constraints.\n- Domain artifacts for {subdomain} (see skill references/).\n\n## Optional Inputs\n- Existing reports, prior run manifests, tool availability notes.\n\n## Prerequisites\n- `axiom doctor --skip-tests` green; relevant base skills loaded.\n\n## Execution Workflow\n1. Normalize the request into objective, scope, and constraints.\n2. Inspect repo context and existing {subdomain} artifacts.\n3. Select method/template from this skill.\n4. Generate or modify artifacts (dry-run first).\n5. Validate structurally and semantically (scripts/ + checklists/).\n6. Run applicable checks; record results.\n7. Produce traceability and review evidence.\n8. Summarize assumptions, risks, next actions.\n\n## Tool Invocations\n- `run_skill` with structured context; dry-run before writes.\n- `validate_skill` must pass before release use.\n- MCP tools: {mcp}.\n\n## Decision Rules\n- Prefer explicit configuration over invented defaults; flag every assumption.\n- Safety/security-relevant outputs require human review (review_required: true).\n\n## Workflow\nFollow Execution Workflow; record per-step evidence in the run manifest.\n\n## Deliverables\n- Run report under `.axiom/runs/<timestamp>/{sid}/`.\n- Skill-specific artifacts listed in catalog outputs.\n\n## Acceptance Criteria\n- `validate_skill` passes; checklist gates all green; traceability complete.\n\n## Acceptance\n- All checklist gates pass; findings carry severity + evidence + action.\n\n## Validation Procedure\n1. `python scripts/validate_skills.py --skill {sid}`.\n2. Review checklist gates.\n3. Human review for high/safety-critical risk levels.\n\n## Common Failure Modes\n- Missing inputs invented instead of flagged -> require explicit inputs.\n- Unreviewed safety/security output merged -> block at review gate.\n\n## Guardrails\n- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.\n- Never claim certification or compliance from heuristic checks.\n\n## References\n- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.\n"""

MANIFEST = """id: {sid}\nversion: 1.2.0\ncontract_version: 1\ntype: reusable-skill\nsource_of_truth:\n  instructions: SKILL.md\n  contract: manifest.yaml\nfacets:\n  domains:\n  - {domain}\n  platforms:\n{plats}standards:\n{stds}axiom:\n  dotted_name: axiom.{domain}.{short}\n  maturity: {maturity}\n  category: {category}\n"""


def build() -> dict[str, pathlib.Path]:
    tmpl = (ROOT / "skills" / "_templates" / "SKILL.template.md").read_text()
    _ = tmpl
    written: dict[str, pathlib.Path] = {}
    for s in SKILLS:
        d = ROOT / "skills" / s["id"]
        d.mkdir(parents=True, exist_ok=True)
        fm = {"name": s["id"], "title": s["title"], "description": s["desc"],
              "version": "0.1.0", "author": "PRATIK PATIL", "license": "Apache-2.0",
              "domains": ["automotive" if s["domain"] == "automotive" else s["domain"] if s["domain"] != "cross-domain" else "all"],
              "platforms": s["platforms"]}
        if s["domain"] == "platform":
            fm["domains"] = ["all"]
        fm_lines = ["name: " + s["id"], "title: " + s["title"],
                    "description: >",
                    "  " + s["desc"],
                    "version: 0.1.0", "author: PRATIK PATIL",
                    "license: Apache-2.0",
                    "domains: [" + ", ".join(fm["domains"]) + "]",
                    "platforms: [" + ", ".join(s["platforms"]) + "]",
                    "axiom:",
                    "  dotted_name: axiom." + s["domain"] + "." + s["id"].replace("axiom-", "").replace("-", "."),
                    "  domain: " + s["domain"],
                    "  subdomain: " + s["subdomain"],
                    "  category: " + s["category"],
                    "  maturity: " + s["maturity"],
                    "  owner: axiom-embedded",
                    "  tags: [" + s["subdomain"] + "]",
                    "  related_skills: []",
                    "  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]",
                    "  standards: [" + ", ".join(s["standards"]) + "]",
                    "  artifact_types: [" + ", ".join(s["artifacts"]) + "]",
                    "  mcp_tools: [run_skill, validate_skill]",
                    "  risk_level: " + ("safety-critical" if s["risk"] == "safety-critical" else s["risk"]),
                    "  review_required: true",
                    "  safety_critical: " + ("true" if s["risk"] == "safety-critical" else "false"),
                    "  inputs: [repository path, target files, objective, constraints]",
                    "  outputs: [run report, run manifest]",
                    "  required_tools: [validate_skill]",
                    "  optional_tools: [run_skill]"]
        body = SKILL_MD.format(name="\n".join(fm_lines), title=s["title"],
                               desc=s["desc"], subdomain=s["subdomain"],
                               domain=s["domain"], maturity=s["maturity"],
                               title_lower=s["title"].lower(),
                               mcp="run_skill, validate_skill",
                               sid=s["id"])
        p = d / "SKILL.md"
        if not p.exists():
            p.write_text(body, encoding="utf-8")
            written[s["id"]] = p
        plats = "".join(f"  - {pl}\n" for pl in s["platforms"])
        stds = "".join(f"  - {st}\n" for st in s["standards"]) or "  []\n"
        mp = d / "manifest.yaml"
        if not mp.exists():
            short = s["id"].replace("axiom-", "").replace("-", "_")
            mp.write_text(MANIFEST.format(sid=s["id"], domain=fm["domains"][0],
                                          plats=plats, stds=stds,
                                          maturity=s["maturity"],
                                          category=s["category"], short=short),
                          encoding="utf-8")
        ck = d / "checklists" / "review.yaml"
        ck.parent.mkdir(exist_ok=True)
        if not ck.exists():
            ck.write_text("gates:\n  - id: scope\n    text: Scope, inputs, prerequisites recorded\n  - id: method\n    text: Workflow steps executed with evidence\n  - id: validation\n    text: Scripts + checklist gates green\n  - id: traceability\n    text: Links complete\n  - id: review\n    text: Human review done for safety/security output\n",
                          encoding="utf-8")
        (d / "references").mkdir(exist_ok=True)
        (d / "templates").mkdir(exist_ok=True)
        (d / "scripts").mkdir(exist_ok=True)
        (d / "tests").mkdir(exist_ok=True)
    # catalog.yaml
    cat = {"schema_version": "1.0",
           "skills": [{"id": s["id"], "name": "axiom." + s["domain"] + "." + s["id"].replace("axiom-", "").replace("-", "."),
                       "title": s["title"], "version": "0.1.0",
                       "domain": s["domain"], "subdomain": s["subdomain"],
                       "category": s["category"], "maturity": s["maturity"],
                       "owner": "axiom-embedded", "tags": [s["subdomain"]],
                       "inputs": ["repository path", "target files", "objective", "constraints"],
                       "outputs": ["run report", "run manifest"],
                       "dependencies": [], "related_skills": [],
                       "path": "skills/" + s["id"], "enabled": True} for s in SKILLS]}
    (ROOT / "skills" / "catalog.yaml").write_text(
        yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")
    # registry.yaml (prompt2 shape)
    reg = {"version": 1,
           "skills": [{"name": "axiom." + s["domain"] + "." + s["id"].replace("axiom-", "").replace("-", "."),
                       "path": "skills/" + s["id"], "domain": s["domain"],
                       "maturity": s["maturity"]} for s in SKILLS]}
    (ROOT / "skills" / "registry.yaml").write_text(
        yaml.safe_dump(reg, sort_keys=False), encoding="utf-8")
    return written


def check() -> int:
    missing = []
    for s in SKILLS:
        for rel in ("SKILL.md", "manifest.yaml", "checklists/review.yaml"):
            if not (ROOT / "skills" / s["id"] / rel).exists():
                missing.append(f"skills/{s['id']}/{rel}")
    for f in ("skills/catalog.yaml", "skills/registry.yaml"):
        if not (ROOT / f).exists():
            missing.append(f)
    if missing:
        print("MISSING:")
        for m in missing:
            print(f"- {m}")
        return 1
    print(f"scaffold OK: {len(SKILLS)} skills")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(check())
    w = build()
    print(f"scaffolded {len(w)} new SKILL.md files ({len(SKILLS)} total in catalog)")
