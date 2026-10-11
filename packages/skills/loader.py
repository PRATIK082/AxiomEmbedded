"""Skill loader: parse SKILL.md frontmatter safely, validate contract, resolve files."""
from __future__ import annotations
import pathlib
import re
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VER_RE = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED_FM = {"name", "description", "version", "domains", "platforms"}
MATURITIES = {"experimental", "beta", "production"}


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
    ax = fm.get("axiom", {}) or {}
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
    else:
        warnings.append("no axiom: metadata block (legacy skill)")
    # required sections in body
    for section in ("## Purpose", "## Workflow", "## Acceptance"):
        if section.lower() not in s["body"].lower():
            warnings.append(f"body missing section {section}")
    return {"skill": skill_id, "valid": not errors, "errors": errors,
            "warnings": warnings}
