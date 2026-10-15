"""Project-context resolver: how every agent self-understands the project.

Resolution order (highest priority first):
  1. Explicit file: ./axiom.project.yaml or ./.axiom/project.yaml (confidence 1.0)
  2. Repo signals + prompt keywords combined:
     - agree -> confidence 0.9, no clarification
     - prompt-domain differs from weak repo-domain -> union slice + clarification
     - single signal -> confidence 0.65
  3. Nothing detected -> fallback generic-embedded, confidence 0.2,
     needs_clarification=True (agent MUST ask, never guess blindly).

Token rule: resolver returns a load_plan {core, primary, deferred} built from
configs/domain-routing.yaml priority_skills + skill_groups, capped by
runtime.token_budget so agents open at most primary_cap SKILL.md files up
front. Prompt-domain extras are appended to primary (dedup, still capped;
overflow goes to deferred).

Production rule: callers must echo domain_used/skills_loaded/skills_deferred
in the final verdict block (see runtime.production_output_contract).
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


def build_load_plan(
    agent_id: str,
    domain: str,
    prompt_domain: str | None = None,
    routing: dict | None = None,
) -> dict:
    """Core + primary + deferred skill lists honoring the token budget."""
    import json as _json

    routing = routing or load_routing()
    runtime = (routing or {}).get("runtime", {}) or {}
    budget = runtime.get("token_budget", {}) or {}
    primary_cap = int(budget.get("primary_cap", 8))
    group_cap = int(budget.get("group_cap", 12))
    domains = (routing or {}).get("domains", {}) or {}
    binding = (routing or {}).get("agent_binding", {}) or {}
    core = (binding.get("core_skill_by_agent", {}) or {}).get(agent_id)
    try:
        index = _json.loads((ROOT / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    except Exception:
        index = {"skills": {}, "by_group": {}}
    skills_index = index.get("skills", {}) or {}
    by_group = index.get("by_group", {}) or {}

    def domain_skills(dom: str | None) -> list[str]:
        if not dom or dom not in domains:
            return []
        spec = domains[dom] or {}
        ordered: list[str] = []
        for cand in list(spec.get("priority_skills", []) or []):
            if cand in skills_index and cand not in ordered:
                ordered.append(cand)
        group_seen: list[str] = []
        for group in spec.get("skill_groups", []) or []:
            for skill in by_group.get(group, []) or []:
                if skill in skills_index and skill not in ordered and skill not in group_seen:
                    group_seen.append(skill)
        ordered.extend(sorted(group_seen)[:group_cap])
        return ordered

    # Project slice first, then UNION prompt-domain extras (trigger rule).
    combined = domain_skills(domain)
    if prompt_domain and prompt_domain != domain:
        for extra in domain_skills(prompt_domain):
            if extra not in combined:
                combined.append(extra)
    primary: list[str] = []
    if core and core in skills_index:
        primary.append(core)
    for skill in combined:
        if skill not in primary:
            primary.append(skill)
        if len(primary) >= primary_cap:
            break
    full_ordered = ([core] if core in skills_index else []) + combined
    deferred = [s for s in full_ordered if s not in primary]
    return {"core": core, "primary": primary,
            "deferred": deferred, "prompt_domain": prompt_domain}


def resolve_project_context(
    repo_root: str | pathlib.Path = ".",
    request_text: str = "",
    agent_id: str = "engineering-manager",
) -> dict:
    """Return {domain, prompt_domain, platform, standards, profile, source,
    confidence, needs_clarification, clarification_question, load_plan}."""
    routing = load_routing()
    defaults = (routing or {}).get("defaults", {})
    runtime = (routing or {}).get("runtime", {}) or {}
    domains = (routing or {}).get("domains", {})
    ask_threshold = float(runtime.get("ask_threshold", 0.5))

    explicit = read_explicit_project(repo_root)
    if explicit:
        domain = str(explicit.get("domain", "")).lower() or None
        domain = domain or defaults.get("fallback_domain", "generic-embedded")
        spec = domains.get(domain, {}) if domain else {}
        prompt_domain = detect_domain(request_text or "")
        load_plan = build_load_plan(agent_id, domain, prompt_domain, routing)
        needs_clar = bool(prompt_domain and prompt_domain != domain)
        question = None
        if needs_clar:
            template = str(runtime.get("clarification_question", ""))
            question = template.format(
                repo_domain=domain, prompt_domain=prompt_domain,
                candidates=f"{domain}, {prompt_domain}")
            # Union extras already inside load_plan; surface both domains.
            load_plan["conflict"] = {"repo_domain": domain, "prompt_domain": prompt_domain}
        return {
            "domain": domain, "prompt_domain": prompt_domain,
            "platform": explicit.get("platform") or (spec.get("platforms", [None])[0]),
            "os": explicit.get("os"), "standards": explicit.get("standards") or spec.get("standards", []),
            "profile": explicit.get("profile") or spec.get("default_profile"),
            "source": f"explicit:{explicit.get('_source')}",
            "confidence": 1.0 if not needs_clar else 0.7,
            "needs_clarification": needs_clar,
            "clarification_question": question,
            "load_plan": load_plan,
        }

    repo_domain = detect_repo_signals(repo_root, routing)
    prompt_domain = detect_domain(request_text or "")
    if repo_domain and prompt_domain and repo_domain == prompt_domain:
        domain, confidence, clar, source = repo_domain, 0.9, False, "repo+prompt-agree"
    elif repo_domain and prompt_domain and repo_domain != prompt_domain:
        # Conflict: keep repo as project domain, union prompt extras, ASK user.
        domain, confidence, clar, source = repo_domain, 0.55, True, "repo-prompt-conflict"
    elif repo_domain or prompt_domain:
        domain = repo_domain or prompt_domain
        confidence, clar = 0.65, False
        source = "repo-signals" if repo_domain else "prompt-keywords"
    else:
        domain = defaults.get("fallback_domain", "generic-embedded")
        confidence, clar, source = 0.2, True, "fallback"
    spec = domains.get(domain, {}) if isinstance(domains, dict) else {}
    load_plan = build_load_plan(agent_id, domain, prompt_domain, routing)
    question = None
    if clar or confidence < ask_threshold:
        clar = True
        if repo_domain and prompt_domain and repo_domain != prompt_domain:
            template = str(runtime.get("clarification_question", ""))
            question = template.format(
                repo_domain=repo_domain, prompt_domain=prompt_domain,
                candidates=f"{repo_domain}, {prompt_domain}, generic-embedded")
            load_plan["conflict"] = {"repo_domain": repo_domain, "prompt_domain": prompt_domain}
        else:
            question = (f"No confident project signal found (best guess: {domain}). "
                        f"Which domain/platform should I use? Reply with domain and "
                        f"platform, e.g. 'automotive, mcu'.")
    return {
        "domain": domain, "prompt_domain": prompt_domain,
        "platform": (spec.get("platforms", [None])[0]) if spec else None,
        "os": None, "standards": spec.get("standards", []) if spec else [],
        "profile": spec.get("default_profile") if spec else defaults.get("fallback_profile"),
        "source": source, "confidence": confidence,
        "needs_clarification": clar, "clarification_question": question,
        "load_plan": load_plan,
    }
