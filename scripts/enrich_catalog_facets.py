"""Backfill prompt2 discovery facets into skills/catalog.yaml from SKILL.md axiom: blocks.

SKILL.md frontmatter stays the single source of truth; this script only copies
lifecycle/standards/artifact_types/mcp_tools/risk_level/review_required into the
matching catalog entries (axiom-* skills). Idempotent. Usage:
  python scripts/enrich_catalog_facets.py [--check]
"""
from __future__ import annotations
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
FACETS = ("lifecycle", "standards", "artifact_types", "mcp_tools",
          "risk_level", "review_required")
# DESA Phase 2 facets: canonical names stored in catalog.yaml.
DESA_FACETS = ("activity", "capability_kind", "primary_domain",
               "risk_class", "lifecycle_phases", "standard_ids")
# axiom: block aliases accepted for backward compatibility.
DESA_ALIASES = {
    "activity": ("activity",),
    "capability_kind": ("capability_kind", "capability-kind", "type"),
    "primary_domain": ("primary_domain", "domain"),
    "risk_class": ("risk_class", "risk_level"),
    "lifecycle_phases": ("lifecycle_phases", "lifecycle"),
    "standard_ids": ("standard_ids", "standards"),
}


def load_fm(skill_id: str) -> dict:
    text = (ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1]) or {}


# Fallback activity inference (DESA Phase 5): skills whose SKILL.md axiom:
# block carries no activity get a deterministic mapping from skill-id
# keywords. Ordered: specific before general. Reviewable; extend deliberately.
ACTIVITY_KEYWORDS: tuple[tuple[str, ...], str] = (
    (("requirements-traceability", "traceability"), "requirements-traceability"),
    (("requirements-review",), "requirements-review"),
    (("requirements-derivation", "derivation", "decomposition"), "requirements-derivation"),
    (("requirements-allocation", "allocation"), "requirements-allocation"),
    (("requirements-analysis", "requirements", "srs", "shall"), "requirements-analysis"),
    (("safety-review",), "safety-review"),
    (("security-review",), "security-review"),
    (("functional-safety", "hazard", "fmea", "asil"), "functional-safety"),
    (("cybersecurity", "threat", "tara", "ids", "firewall"), "cybersecurity"),
    (("sil-hil",), "sil-hil"),
    (("integration-testing", "integration-test"), "integration-testing"),
    (("system-testing", "system-test"), "system-testing"),
    (("unit-testing", "unit-test"), "unit-testing"),
    (("code-review",), "code-review"),
    (("coding-guidelines", "coding", "misra", "cert-c", "guideline"), "coding-guidelines"),
    (("configuration-management", "arxml", "ecuc", "config"), "configuration-management"),
    (("standards-applicability", "applicability", "compliance"), "standards-applicability"),
    (("process-assessment", "aspice", "spice", "assessment", "audit"), "process-assessment"),
    (("release-readiness", "release", "deployment", "production-readiness"), "release-readiness"),
    (("validation",), "validation"),
    (("verification", "verify"), "verification"),
    (("documentation", "doxygen", "sphinx", "manual"), "documentation"),
    (("debugging", "debug", "gdb", "diagnosing"), "debugging"),
    (("architecture", "architect", "design"), "architecture"),
    # Domain-safety religions: machinery/rail/medical safety standards.
    (("en50128", "en-50128", "rail"), "functional-safety"),
    (("iec62061", "iec-62061", "iso13849", "iso-13849", "machinery-safety",
      "loto", "pfl-plan", "operating-envelope", "iso15066", "iso-15066"), "functional-safety"),
    (("medical", "iec62304", "iec-62304"), "process-assessment"),
    # Robotics/industrial/agentic fallback vocabulary.
    (("e2e", "playwright", "performance-test", "test-catalog"), "system-testing"),
    (("conformity", "declaration"), "standards-applicability"),
    (("lifecycle", "vcycle", "training-matrix", "human-in-the-loop"), "process-assessment"),
    (("red-team",), "security-review"),
    (("evaluation", "eval"), "verification"),
    (("observability", "monitoring"), "debugging"),
    (("hardware-aware",), "verification"),
    (("asset-inventory", "prompt-injection"), "cybersecurity"),
    (("explainer", "coauthoring", "document-skills", "model-card"), "documentation"),
    # Third pass: remaining vocabulary.
    (("diagnostics", "doip", "acceptance", "fault-injection"), "validation"),
    (("hil",), "sil-hil"),
    (("safety",), "functional-safety"),
    (("security", "secure"), "cybersecurity"),
    (("spec", "scope", "sop"), "requirements-analysis"),
    (("skill",), "process-assessment"),
    (("sre", "reliability"), "process-assessment"),
    (("layout",), "architecture"),
    (("generator",), "documentation"),
    (("storage", "memory"), "verification"),
    (("test",), "unit-testing"),
    (("change-impact", "impact", "evidence"), "process-assessment"),
    (("change-impact", "impact", "evidence"), "process-assessment"),
    (("static-analysis", "coverage", "performance"), "verification"),
    (("trace-analysis",), "debugging"),
    (("radiation", "hardening", "space"), "implementation"),
    (("telecom", "5g", "modem", "terraform", "infra", "websocket",
      "wireless", "conduit", "zone", "bare-metal", "build", "mpsoc",
      "mpu", "soc", "bringup", "feature", "legacy", "codebase",
      "simulation"), "implementation"),
    (("implementation", "driver", "bsw", "mcal", "hal", "rtos", "freertos",
      "ethernet", "eth", "can", "lin", "flexray", "uds", "xcp", "j1939",
      "bootloader", "boot", "flash", "nvm", "eeprom", "crypto", "mcu",
      "peripheral", "gpio", "uart", "spi", "i2c", "adc", "pwm", "timer",
      "dma", "interrupt", "bsp", "middleware", "stack", "autosar",
      "do-178", "do-254", "do-326", "arp4754", "robotics", "ros",
      "industrial", "iec-61", "iec62443", "aerospace",
      "qnx", "zephyr", "embedded", "sensor", "actuator", "motor",
      "adas", "cockpit", "body-", "ota", "networks", "uav", "ros2",
      "framework-", "mcp-", "cli-developer", "kubernetes", "edge",
      "database", "legacy-modernizer", "orchestration", "context-",
      "prompt", "slop", "commit-plan", "energy-grid", "chaos", "git",
      "automotive", "body"), "implementation"),
)


# "-review" suffixed skills lift the base activity into its review counterpart.
REVIEW_LIFT = {
    "functional-safety": "safety-review",
    "cybersecurity": "security-review",
    "implementation": "code-review",
    "architecture": "code-review",
    "requirements-analysis": "requirements-review",
    "requirements-derivation": "requirements-review",
    "requirements-allocation": "requirements-review",
    "requirements-traceability": "requirements-review",
    "documentation": "code-review",
}


def infer_activity(skill_id: str, title: str = "") -> str:
    sid = skill_id.lower()
    if sid.endswith("-review"):
        base = infer_activity(sid[: -len("-review")], title)
        return REVIEW_LIFT.get(base, base or "code-review")
    hay = f"{sid} {title}".lower()
    for keywords, activity in ACTIVITY_KEYWORDS:
        if any(k in hay for k in keywords):
            return activity
    return ""


def _desa_want(ax: dict, facet: str):
    for alias in DESA_ALIASES.get(facet, (facet,)):
        if alias in ax and ax[alias] is not None:
            val = ax[alias]
            # risk_class defaults to risk_level medium; normalize safety flags.
            if facet == "risk_class" and val == "medium":
                pass
            return val
    if facet in ("activity", "capability_kind"):
        return ""
    if facet in ("lifecycle_phases", "standard_ids"):
        return []
    if facet == "primary_domain":
        return str(ax.get("domain", "generic-embedded"))
    if facet == "risk_class":
        return str(ax.get("risk_level", "medium"))
    return ""


def enrich(check: bool = False) -> int:
    cat_p = ROOT / "skills" / "catalog.yaml"
    cat = yaml.safe_load(cat_p.read_text(encoding="utf-8"))
    drift = []
    for entry in cat["skills"]:
        sid = entry["id"]
        is_axiom = sid.startswith("axiom-")
        try:
            ax = (load_fm(sid).get("axiom") or {})
        except Exception:
            ax = {}
        if is_axiom:
            for facet in FACETS:
                want = ax.get(facet, [] if facet not in ("risk_level",) else "medium")
                if facet == "risk_level" and want is None:
                    want = "medium"
                if entry.get(facet) != want:
                    drift.append(f"{sid}.{facet}")
                    if not check:
                        entry[facet] = want
        for facet in DESA_FACETS:
            want = _desa_want(ax, facet) if ax else None
            if facet == "activity" and not want:
                want = infer_activity(sid, entry.get("title", ""))
            elif facet == "capability_kind" and not want:
                want = "domain-specific" if is_axiom else "general"
            elif facet == "primary_domain" and not want:
                want = str(entry.get("domain", "generic-embedded"))
            elif facet == "risk_class" and not want:
                want = "medium"
            elif facet in ("lifecycle_phases", "standard_ids") and want is None:
                want = []
            if entry.get(facet) != want:
                drift.append(f"{sid}.{facet}")
                if not check:
                    entry[facet] = want
    if check:
        if drift:
            print("FACET DRIFT:")
            for d in drift:
                print(f"- {d}")
            return 1
        print(f"facet parity OK: {len(cat['skills'])} entries")
        return 0
    cat_p.write_text(yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")
    print(f"enriched {len(drift)} facet fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(enrich("--check" in sys.argv))
