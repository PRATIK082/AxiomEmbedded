# SPDX-License-Identifier: Apache-2.0
"""Deep-research pipeline: planner -> searchers -> verifier -> synthesizer.

Primary search runs through OpenCode subagents (``axiom oc`` isolated
config); deterministic fallbacks keep ``axiom research`` useful with no
binary, no keys, and no network:

- ``opencode`` backend: one ``opencode run --agent skill-researcher``
  per sub-question under the Axiom-isolated config.
- ``local`` backend: keyword search over this checkout's ``skills/*/``
  manifests (structured ``standards_refs`` carry number/version/clause/
  source_url) plus ``agents/*/`` frontmatter. Always available.
- ``tavily`` / ``brave`` / ``searxng`` backends: key-gated web search.
  Without ``TAVILY_API_KEY`` / ``BRAVE_API_KEY`` / ``SEARXNG_URL`` they
  report ``unavailable`` honestly instead of fabricating findings.

Guards (audit §Phase 3): every report ends with SAFETY_NOTICE (a passing
check is not certification); standards text is paraphrase-only (local
findings quote at most QUOTE_LIMIT characters and carry identifiers,
never normative prose).
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess

from packages.installer import find_content_source

SAFETY_NOTICE = (
    "Safety boundary: AxiomEmbedded provides engineering process automation "
    "and reference checks. A research finding is not a certification result "
    "and must not be represented as proof of compliance, safety integrity, "
    "security certification, or airworthiness. The adopting project must "
    "determine applicable editions, objectives, independence requirements, "
    "and evidence with qualified personnel and authorised tools."
)

QUOTE_LIMIT = 200
DEFAULT_MAX_SUBQUESTIONS = 3
BACKENDS = ("auto", "opencode", "local", "tavily", "brave", "searxng")

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_/][a-z0-9]+)*")
_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "for", "in", "on", "to", "with",
    "what", "which", "how", "is", "are", "be", "by", "vs", "compare",
    "between", "do", "does",
})


def plan(question: str, max_subquestions: int = DEFAULT_MAX_SUBQUESTIONS) -> list[str]:
    """Split a question into focused sub-questions (deterministic, local)."""
    text = (question or "").strip()
    if not text:
        return []
    parts = [p.strip() for p in re.split(r"[?;]|\bvs\b|\bversus\b", text) if p.strip()]
    if len(parts) <= 1:
        words = [w for w in _TOKEN_RE.findall(text.lower()) if w not in _STOPWORDS]
        seen: list[str] = []
        for word in words:
            if word not in seen:
                seen.append(word)
        core = " ".join(seen[:8]) or text
        parts = [text, f"{core} standards and clauses", f"{core} verification approach"]
    return parts[:max(1, max_subquestions)]


def _keywords(text: str) -> set[str]:
    return {w for w in _TOKEN_RE.findall(text.lower()) if w not in _STOPWORDS}


def _skill_text(skill_dir: pathlib.Path) -> str:
    chunks = [skill_dir.name]
    manifest = skill_dir / "manifest.yaml"
    if manifest.is_file():
        chunks.append(manifest.read_text(encoding="utf-8", errors="replace")[:2000])
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        for line in skill_md.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("#"):
                chunks.append(line.lstrip("# ").strip())
    return "\n".join(chunks)


def search_local(subquestion: str, source: str | pathlib.Path | None = None) -> dict:
    """Search checkout skills/agents for a sub-question; always available."""
    try:
        content = find_content_source(source)
    except ValueError as exc:
        return {"backend": "local", "status": "unavailable", "reason": str(exc),
                "findings": []}
    keywords = _keywords(subquestion)
    scored: list[tuple[int, pathlib.Path, list[dict]]] = []
    skills_root = content / "skills"
    if skills_root.is_dir():
        for skill_dir in sorted(skills_root.iterdir()):
            if not skill_dir.is_dir():
                continue
            haystack = _skill_text(skill_dir).lower()
            score = sum(1 for kw in keywords if kw in haystack)
            if score == 0:
                continue
            refs: list[dict] = []
            manifest = skill_dir / "manifest.yaml"
            if manifest.is_file():
                try:
                    import yaml  # type: ignore[import]

                    refs = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
                    refs = refs.get("standards_refs", []) or []
                except Exception:
                    refs = []
            scored.append((score, skill_dir, [r for r in refs if str(r.get("number", "")).strip()]))
    if not scored:
        return {"backend": "local", "status": "ok", "findings": []}
    best = max(score for score, _, _ in scored)
    # Relative threshold: multi-keyword queries drop 1-hit noise; single-keyword
    # queries still match. Cap keeps reports readable.
    floor = 2 if best >= 2 else 1
    ranked = sorted(scored, key=lambda t: (-t[0], t[1].name))[:8]
    findings: list[dict] = []
    for score, skill_dir, refs in ranked:
        if score < floor:
            continue
        rel = f"skills/{skill_dir.name}"
        for ref in refs:
            number = str(ref.get("number", "")).strip()
            findings.append({
                "claim": f"{rel} references {number} "
                         f"{ref.get('version', '')} ({ref.get('clause', '')})".strip(),
                "number": number,
                "version": str(ref.get("version", "")),
                "clause": str(ref.get("clause", "")),
                "source_url": str(ref.get("source_url", "")),
                "source_path": f"{rel}/manifest.yaml",
                "confidence": "high" if ref.get("source_url") else "medium",
                "paraphrase": True,
            })
        findings.append({
            "claim": f"Skill '{skill_dir.name}' matches ({score} keyword hits); "
                     "see its SKILL.md headings for scope (paraphrased, not quoted).",
            "number": "",
            "version": "",
            "clause": "",
            "source_url": "",
            "source_path": f"{rel}/SKILL.md",
            "confidence": "medium",
            "paraphrase": True,
        })
    return {"backend": "local", "status": "ok", "findings": findings}


def _web_stub(name: str, env_var: str, hint: str) -> dict:
    if not os.environ.get(env_var):
        return {"backend": name, "status": "unavailable",
                "reason": f"{env_var} is not set ({hint}).", "findings": []}
    return {"backend": name, "status": "unavailable",
            "reason": f"{name} live search is not wired yet; key present but "
                      "network calls are out of scope for this change.",
            "findings": []}


def search_web(subquestion: str, backend: str) -> dict:
    """Key-gated web backends: honest unavailable without credentials."""
    _ = subquestion
    if backend == "tavily":
        return _web_stub("tavily", "TAVILY_API_KEY", "set it to enable Tavily search")
    if backend == "brave":
        return _web_stub("brave", "BRAVE_API_KEY", "set it to enable Brave search")
    if backend == "searxng":
        return _web_stub("searxng", "SEARXNG_URL", "set it to point at a SearXNG instance")
    raise ValueError(f"unknown web backend: {backend}")


def search_opencode(subquestion: str, *, model: str | None = None,
                    source: str | None = None, timeout: int = 300) -> dict:
    """Run one sub-question via the skill-researcher OpenCode subagent."""
    from packages import launcher as _launcher

    status = _launcher.opencode_status()
    if status["state"] == "fail":
        return {"backend": "opencode", "status": "unavailable",
                "reason": status["detail"], "findings": []}
    cfg = _launcher.ensure_isolated_config(model=None, source=source)
    env = _launcher.launch_env(config_file=cfg["config_file"],
                               config_dir=cfg["config_dir"])
    prompt = ("Research only: investigate and report. Do not modify, create, "
              "or delete any files. Emit one Finding JSON object per claim "
              "(claim, number, version, clause, source_url), then a short "
              "summary.\n\n" + subquestion)
    argv = [status["binary"], "run", prompt, "--agent", "skill-researcher",
            "--format", "json"]
    if model:
        argv.extend(["--model", model])
    try:
        proc = subprocess.run(argv, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except Exception as exc:
        return {"backend": "opencode", "status": "error",
                "reason": f"opencode run failed: {exc}", "findings": []}
    findings: list[dict] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("claim"):
            obj.setdefault("confidence", "medium" if obj.get("source_url") else "low")
            obj["paraphrase"] = True
            findings.append(obj)
    state = "ok" if proc.returncode == 0 else "error"
    result: dict = {"backend": "opencode", "status": state, "findings": findings}
    if proc.returncode != 0:
        result["reason"] = (proc.stderr or "")[-500:]
    return result


def verify(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Dedupe + confidence-gate findings; drop uncited claims honestly."""
    accepted: list[dict] = []
    rejected: list[dict] = []
    seen: set[str] = set()
    for finding in findings:
        key = (str(finding.get("source_url") or finding.get("source_path") or ""),
               str(finding.get("claim", ""))[:QUOTE_LIMIT])
        if key in seen:
            rejected.append({**finding, "reject_reason": "duplicate"})
            continue
        seen.add(key)
        if finding.get("confidence") == "low" or (
                not finding.get("source_url") and not finding.get("source_path")):
            rejected.append({**finding, "reject_reason": "uncited claim (no source)"})
            continue
        accepted.append(finding)
    return accepted, rejected


def synthesize(question: str, per_question: list[dict],
               accepted: list[dict], rejected: list[dict]) -> str:
    """Render the markdown research report (paraphrase-only, safety-noticed)."""
    lines = [f"# Research: {question}", ""]
    lines.append("## Method")
    for entry in per_question:
        backend = entry.get("backend", "?")
        status = entry.get("status", "?")
        note = entry.get("reason", f"{len(entry.get('findings', []))} raw findings")
        lines.append(f"- `{backend}`: {status} — {note}")
    lines.append("")
    lines.append("## Findings")
    if not accepted:
        lines.append("No cited findings. Backends were unavailable or returned "
                     "only uncited claims (listed under Rejected).")
    for finding in accepted:
        claim = str(finding.get("claim", ""))[:QUOTE_LIMIT]
        lines.append(f"- [{finding.get('confidence', '?')}] {claim}")
        cite = finding.get("source_url") or finding.get("source_path", "")
        meta = " ".join(p for p in (str(finding.get("number", "")),
                                    str(finding.get("version", "")),
                                    str(finding.get("clause", ""))) if p).strip()
        if meta:
            cite = f"{meta} — {cite}" if cite else meta
        if cite:
            lines.append(f"  Source: {cite}")
    lines.append("")
    lines.append("## Rejected (uncited or duplicate)")
    if not rejected:
        lines.append("None.")
    for finding in rejected:
        lines.append(f"- {str(finding.get('claim', ''))[:QUOTE_LIMIT]} "
                     f"({finding.get('reject_reason', 'rejected')})")
    lines.append("")
    lines.append("## Safety notice")
    lines.append(SAFETY_NOTICE)
    return "\n".join(lines) + "\n"


def run(question: str, *, backend: str = "auto",
        max_subquestions: int = DEFAULT_MAX_SUBQUESTIONS,
        model: str | None = None, source: str | None = None) -> dict:
    """Full pipeline; returns a JSON-serialisable envelope."""
    if backend not in BACKENDS:
        raise ValueError(f"unknown backend: {backend} (choose from {BACKENDS})")
    subquestions = plan(question, max_subquestions)
    if not subquestions:
        return {"status": "error", "question": question,
                "message": "empty question", "findings": []}

    def search_one(sub: str, which: str) -> dict:
        if which == "opencode":
            return search_opencode(sub, model=model, source=source)
        if which in ("tavily", "brave", "searxng"):
            return search_web(sub, which)
        return search_local(sub, source)

    per_question: list[dict] = []
    raw: list[dict] = []
    seen_claims: set[tuple[str, str]] = set()
    for sub in subquestions:
        which = backend
        if which == "auto":
            first = search_opencode(sub, model=model, source=source)
            if first["status"] == "unavailable":
                local = search_local(sub, source)
                local["note"] = f"opencode unavailable: {first.get('reason', '')}"
                result = local
            else:
                result = first
                which = "opencode"
        else:
            result = search_one(sub, which)
            if result["status"] == "unavailable" and which != "local":
                fallback = search_local(sub, source)
                fallback["note"] = (f"{which} unavailable: {result.get('reason', '')}; "
                                    "fell back to local")
                result = fallback
        per_question.append({"subquestion": sub, **result})
        for finding in result.get("findings", []):
            # Same skill manifest matches several overlapping sub-questions;
            # keep the first occurrence instead of reporting noise duplicates.
            key = (str(finding.get("source_url") or finding.get("source_path") or ""),
                   str(finding.get("claim", ""))[:QUOTE_LIMIT])
            if key not in seen_claims:
                seen_claims.add(key)
                raw.append(finding)
    accepted, rejected = verify(raw)
    report = synthesize(question, per_question, accepted, rejected)
    return {
        "status": "ok",
        "question": question,
        "backend": backend,
        "subquestions": [p["subquestion"] for p in per_question],
        "methods": [{k: p.get(k) for k in ("subquestion", "backend", "status",
                                           "reason", "note") if k in p}
                    for p in per_question],
        "findings": accepted,
        "rejected": rejected,
        "report": report,
    }
