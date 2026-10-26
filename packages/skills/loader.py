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


def load_skill_meta(skill_id: str) -> dict:
    """Lazy: frontmatter + manifest only, body omitted (load on demand)."""
    if not ID_RE.match(skill_id) or ".." in skill_id or "/" in skill_id:
        raise ValueError(f"invalid skill id: {skill_id!r}")
    d = ROOT / "skills" / skill_id
    text = (d / "SKILL.md").read_text(encoding="utf-8")
    fm, _body = parse_skill_doc(text)
    manifest = {}
    mp = d / "manifest.yaml"
    if mp.exists():
        manifest = yaml.safe_load(mp.read_text(encoding="utf-8")) or {}
    return {"id": skill_id, "frontmatter": fm, "manifest": manifest, "dir": str(d),
            "body_loaded": False}


def load_skill_body(skill_id: str) -> str:
    """Load only the body of a skill on demand (lazy loading)."""
    if not ID_RE.match(skill_id) or ".." in skill_id or "/" in skill_id:
        raise ValueError(f"invalid skill id: {skill_id!r}")
    d = ROOT / "skills" / skill_id
    _fm, body = parse_skill_doc((d / "SKILL.md").read_text(encoding="utf-8"))
    return body


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

TEMPLATE_SECTIONS = ("## Purpose", "## Workflow", "## Acceptance", "## Checklist",
                     "## Examples", "## Pitfalls", "## References")


def validate_template(skill_id: str) -> dict:
    errors = []
    warnings = []
    try:
        s = load_skill(skill_id)
    except Exception as exc:
        return {"skill": skill_id, "valid": False, "errors": [str(exc)], "warnings": []}
    fm = s["frontmatter"]
    body = s["body"]
    for sec in ("## Purpose", "## Workflow", "## Acceptance"):
        if sec.lower() not in body.lower():
            warnings.append("body missing section " + sec)
    for sec in ("## Checklist", "## Examples", "## Pitfalls", "## References"):
        if sec.lower() not in body.lower():
            warnings.append("body missing optional section " + sec)
    meta = fm.get("metadata", {}) or {}
    if not meta.get("origin"):
        warnings.append("frontmatter missing metadata.origin")
    if not meta.get("version"):
        warnings.append("frontmatter missing metadata.version")
    ax = fm.get("axiom", {}) or {}
    if "triggers" not in fm and "triggers" not in ax:
        warnings.append("no triggers declared")
    return {"skill": skill_id, "valid": not errors, "errors": errors, "warnings": warnings}
