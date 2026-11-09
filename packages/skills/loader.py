"""Skill loader: parse SKILL.md frontmatter safely, validate contract, resolve files."""
from __future__ import annotations
import pathlib
import re
import yaml

from packages.paths import ROOT
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VER_RE = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED_FM = {"name", "description", "version", "domains", "platforms"}
MATURITIES = {"experimental", "beta", "production"}
VAGUE_TERMS = {"helps with", "processes data", "does stuff", "utility", "helper",
                "misc", "various", "things"}
CONTRACT_FIELDS = {"inputs", "outputs", "risk_level", "review_required",
                   "safety_critical", "lifecycle", "artifact_types", "related_skills"}


def parse_skill_doc(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter ---")
    _, fm_text, body = text.split("---\n", 2)
    fm = yaml.safe_load(fm_text) or {}
    return fm, body


def load_skill(skill_id: str) -> dict:
    if not ID_RE.match(skill_id) or ".." in skill_id or "/" in skill_id:
        raise ValueError(f"invalid skill id: {skill_id!r}")
    d = ROOT / "skills" / skill_id
    fm, body = parse_skill_doc((d / "SKILL.md").read_text(encoding="utf-8"))
    manifest = {}
    mp = d / "manifest.yaml"
    if mp.exists():
        manifest = yaml.safe_load(mp.read_text(encoding="utf-8")) or {}
    return {"id": skill_id, "frontmatter": fm, "body": body, "manifest": manifest,
            "dir": str(d)}


def validate_skill_doc(skill_id: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        s = load_skill(skill_id)
    except FileNotFoundError:
        return {"skill": skill_id, "valid": False, "errors": ["SKILL.md not found"],
                "warnings": []}
    except ValueError as exc:
        return {"skill": skill_id, "valid": False, "errors": [str(exc)], "warnings": []}
    fm = s["frontmatter"]
    missing = REQUIRED_FM - set(fm.keys())
    if missing:
        errors.append(f"missing frontmatter keys: {sorted(missing)}")
    if fm.get("name") != skill_id:
        errors.append(f"frontmatter name {fm.get('name')!r} != directory {skill_id!r}")
    if fm.get("version") and not VER_RE.match(str(fm["version"])):
        errors.append(f"bad version {fm.get('version')!r}, want X.Y.Z")
    # description quality (Agent Skills spec + Axiom hardening)
    desc = str(fm.get("description") or "").strip()
    if desc:
        if len(desc) > 1024:
            errors.append(f"description too long ({len(desc)} > 1024)")
        if len(desc) < 20:
            warnings.append("description too short (<20 chars); add what+when")
        low = desc.lower()
        if low.startswith("i ") or low.startswith("i'"):
            warnings.append("description should be third-person, not first-person")
        if any(v in low for v in VAGUE_TERMS):
            warnings.append("description contains vague terms; specify capability + trigger")
        if "use when" not in low and "when " not in low:
            warnings.append("description lacks trigger clause ('Use when...')")
    ax = fm.get("axiom", {}) or {}
    maturity = ax.get("maturity") if ax else None
    if ax:
        if ax.get("maturity") not in MATURITIES:
            errors.append(f"bad axiom.maturity {ax.get('maturity')!r}")
        for f in ("checklists", "templates", "scripts"):
            for ref in ax.get(f, []) or []:
                if not (ROOT / "skills" / skill_id / ref).exists():
                    errors.append(f"missing referenced file: {ref}")
        for rel in ax.get("related_skills", []) or []:
            if not (ROOT / "skills" / rel).exists():
                warnings.append(f"unknown related_skill {rel}")
        declared_tools = list(ax.get("required_tools", []) or []) + \
            list(ax.get("optional_tools", []) or []) + \
            list(ax.get("mcp_tools", []) or [])
        if declared_tools:
            try:
                from axiom_mcp.server import TOOLS as _MCP_TOOLS
                for t in declared_tools:
                    if t not in _MCP_TOOLS:
                        warnings.append(
                            f"tool {t!r} not in MCP registry "
                            f"(linkable later; see docs/mcp-tool-backlog.md)")
            except Exception:
                warnings.append("mcp tool registry unavailable; "
                                "tool links unchecked")
        # safety gating: safety_critical => review_required
        if ax.get("safety_critical") is True and ax.get("review_required") is not True:
            errors.append("safety_critical requires review_required: true")
        # contract fields for beta/production
        if maturity in ("beta", "production"):
            missing_cf = CONTRACT_FIELDS - set(ax.keys())
            if missing_cf:
                (errors if maturity == "production" else warnings).append(
                    f"missing contract fields for {maturity}: {sorted(missing_cf)}")
        # maturity ladder: production requires tests dir
        if maturity == "production":
            if not (ROOT / "skills" / skill_id / "tests").exists():
                warnings.append("production skill missing tests/ directory")
    else:
        warnings.append("no axiom: metadata block (legacy skill)")
    # required sections in body
    for section in ("## Purpose", "## Workflow", "## Acceptance"):
        if section.lower() not in s["body"].lower():
            warnings.append(f"body missing section {section}")
    # progressive disclosure: body <= 500 lines
    body_lines = s["body"].count("\\n") + 1
    if body_lines > 500:
        warnings.append(f"SKILL.md body too long ({body_lines} lines > 500); offload to references/")
    # naming convention check (axiom skills)
    if skill_id.startswith("axiom-") and not re.match(r"^axiom-[a-z0-9]+(-[a-z0-9]+)+$", skill_id):
        warnings.append("axiom skill id should follow axiom-<domain>-<capability>")
    # reference depth: references/ should be flat (one level)
    refdir = ROOT / "skills" / skill_id / "references"
    if refdir.exists():
        for p in refdir.rglob("*"):
            if p.is_file() and p.parent != refdir:
                warnings.append(f"nested reference beyond one level: {p.relative_to(ROOT / 'skills' / skill_id)}")
                break
    return {"skill": skill_id, "valid": not errors, "errors": errors,
            "warnings": warnings}
