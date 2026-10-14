"""Project-context resolver: how every agent self-understands the project.

Resolution order (highest priority first):
  1. Explicit file: ./axiom.project.yaml or ./.axiom/project.yaml
  2. Repo signals: profiles match, repo-signal substrings, README keywords
  3. Prompt keywords via detect_domain()
  4. Fallback: generic-embedded / generic-embedded profile

Agents call resolve_project_context(repo_root, request_text) at Step 0,
then pass domain/platform into engage() to get the skill slice.
"""
from __future__ import annotations

import pathlib

import yaml

from packages.agents.router import detect_domain

ROOT = pathlib.Path(__file__).resolve().parents[2]

ROUTING_FILE = ROOT / "configs" / "domain-routing.yaml"

PROJECT_CANDIDATES = ("axiom.project.yaml", ".axiom/project.yaml")


def load_routing() -> dict:
    try:
        return yaml.safe_load(ROUTING_FILE.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def read_explicit_project(repo_root: str | pathlib.Path) -> dict | None:
    root = pathlib.Path(repo_root)
    for candidate in PROJECT_CANDIDATES:
        path = root / candidate
        if path.exists():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                if data.get("domain"):
                    data["_source"] = candidate
                    return data
            except Exception:
                continue
    return None


def detect_repo_signals(repo_root: str | pathlib.Path, routing: dict | None = None) -> str | None:
    """Scan file names + README for domain repo_signals. First match wins."""
    routing = routing or load_routing()
    domains = (routing or {}).get("domains", {})
    root = pathlib.Path(repo_root)
    corpus_parts: list[str] = []
    try:
        names = [p.name.lower() for p in root.iterdir()]
        corpus_parts.append(" ".join(names[:200]))
    except Exception:
        pass
    for readme in ("README.md", "AGENTS.md", "REPOSITORY_INVENTORY.md"):
        try:
            text = (root / readme).read_text(encoding="utf-8", errors="ignore")[:4000].lower()
            corpus_parts.append(text)
        except Exception:
            continue
    corpus = " ".join(corpus_parts)
    for domain, spec in domains.items():
        for signal in (spec or {}).get("repo_signals", []):
            if signal and signal.lower() in corpus:
                return domain
    # Fall back to keyword scan of the same corpus via prompt detector.
    return detect_domain(corpus)


def resolve_project_context(
    repo_root: str | pathlib.Path = ".",
    request_text: str = "",
) -> dict:
    """Return {domain, platform, os, standards, profile, source}."""
    routing = load_routing()
    defaults = (routing or {}).get("defaults", {})
    domains = (routing or {}).get("domains", {})

    explicit = read_explicit_project(repo_root)
    if explicit:
        domain = str(explicit.get("domain", "")).lower() or None
        spec = domains.get(domain, {}) if domain else {}
        return {
            "domain": domain or defaults.get("fallback_domain", "generic-embedded"),
            "platform": explicit.get("platform") or (spec.get("platforms", [None])[0]),
            "os": explicit.get("os"),
            "standards": explicit.get("standards") or spec.get("standards", []),
            "profile": explicit.get("profile") or spec.get("default_profile"),
            "source": f"explicit:{explicit.get('_source')}",
        }

    repo_domain = detect_repo_signals(repo_root, routing)
    prompt_domain = detect_domain(request_text or "")
    domain = repo_domain or prompt_domain or defaults.get("fallback_domain", "generic-embedded")
    spec = domains.get(domain, {}) if isinstance(domains, dict) else {}
    source = "repo-signals" if repo_domain else ("prompt-keywords" if prompt_domain else "fallback")
    return {
        "domain": domain,
        "platform": (spec.get("platforms", [None])[0]) if spec else None,
        "os": None,
        "standards": spec.get("standards", []) if spec else [],
        "profile": spec.get("default_profile") if spec else defaults.get("fallback_profile"),
        "source": source,
    }
