"""Central path resolution for AxiomEmbedded.

Works in three modes:
  1. Source checkout: content trees (skills/, registries/, ...) live next to
     the code at parents[2]; detected by the presence of skills/ + registries/.
  2. Installed with content: AXIOM_ROOT env var or a sibling `axiom-content`
     directory points at a content tree.
  3. Code-only install: no content tree; callers must degrade gracefully
     (engage/skills return empty/error instead of crashing).

Every module that previously did ``ROOT = Path(__file__).resolve().parents[2]``
should import ``ROOT`` from here.
"""
from __future__ import annotations

import os
import pathlib

def _detect_root() -> pathlib.Path | None:
    env = os.environ.get("AXIOM_ROOT")
    if env:
        p = pathlib.Path(env).expanduser().resolve()
        if (p / "skills").is_dir() and (p / "registries").is_dir():
            return p
    # Source checkout: packages/paths.py -> parents[1] is repo root
    candidate = pathlib.Path(__file__).resolve().parents[1]
    if (candidate / "skills").is_dir() and (candidate / "registries").is_dir():
        return candidate
    # Installed content alongside the package
    for base in (pathlib.Path(__file__).resolve().parents[0],
                 pathlib.Path(__file__).resolve().parents[1]):
        cand = base / "axiom-content"
        if (cand / "skills").is_dir() and (cand / "registries").is_dir():
            return cand
    # Common user-level content cache
    user = pathlib.Path.home() / ".axiom" / "content"
    if (user / "skills").is_dir() and (user / "registries").is_dir():
        return user
    return None

_detected = _detect_root()
ROOT = _detected if _detected is not None else pathlib.Path(__file__).resolve().parents[1]
HAS_CONTENT = _detected is not None

def content_root() -> pathlib.Path | None:
    return _detected

def is_source_checkout() -> bool:
    return ROOT is not None and (ROOT / "pyproject.toml").exists()

def require_root() -> pathlib.Path:
    if ROOT is None:
        raise RuntimeError(
            "Axiom content tree not found. Set AXIOM_ROOT to a checkout, "
            "or install from an sdist (`pip install axiom-embedded --no-binary :all:`).")
    return ROOT
