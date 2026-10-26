"""SBOM generation (CycloneDX-lite JSON) from project + installed packages."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


def generate_sbom(project_root: str | Path, output: str | Path) -> Path:
    root = Path(project_root).resolve()
    components = []
    # project itself
    try:
        data = yaml.safe_load((root / "pyproject.toml").read_text()) if (root / "pyproject.toml").exists() else {}
    except Exception:
        data = {}
    components.append({"type": "application", "name": "axiom-embedded", "version": "0.2.0"})
    # installed python packages
    try:
        out = subprocess.run(["pip", "list", "--format=json"], capture_output=True, text=True)
        pkgs = json.loads(out.stdout) if out.returncode == 0 else []
    except Exception:
        pkgs = []
    for p in pkgs:
        components.append({"type": "library", "name": p.get("name"), "version": p.get("version")})
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(),
                     "component": {"type": "application", "name": "axiom-embedded"}},
        "components": components,
    }
    outp = Path(output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(sbom, indent=2), encoding="utf-8")
    return outp
