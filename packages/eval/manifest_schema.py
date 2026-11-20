"""Run-manifest schema validation (stdlib only)."""
from __future__ import annotations
import json
from pathlib import Path

REQUIRED_TOP = {"skill", "version", "timestamp", "inputs", "selected_tools",
                "decisions", "generated_files", "warnings", "acceptance_checks"}
REQUIRED_INPUTS = {"repo_path", "target_files", "objective", "constraints"}


def validate_manifest(manifest: dict) -> list[str]:
    """Return list of error strings; empty means OK."""
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    missing = REQUIRED_TOP - set(manifest.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
    inputs = manifest.get("inputs")
    if not isinstance(inputs, dict):
        errors.append("inputs must be an object")
    else:
        missing_in = REQUIRED_INPUTS - set(inputs.keys())
        if missing_in:
            errors.append(f"missing input keys: {sorted(missing_in)}")
    for key in ("selected_tools", "decisions", "generated_files", "warnings", "acceptance_checks"):
        if key in manifest and not isinstance(manifest[key], list):
            errors.append(f"{key} must be a list")
    if "skill" in manifest and not isinstance(manifest["skill"], str):
        errors.append("skill must be a string")
    if "version" in manifest and not isinstance(manifest["version"], str):
        errors.append("version must be a string")
    return errors


def validate_manifest_file(path: str | Path) -> list[str]:
    p = Path(path)
    if not p.exists():
        return [f"file not found: {path}"]
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    return validate_manifest(data)
