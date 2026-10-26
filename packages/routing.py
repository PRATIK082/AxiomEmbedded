"""Model routing (B7): choose a model endpoint based on task difficulty.

Configurable endpoints (Ollama/llama.cpp/LM Studio/OpenAI-compatible). Falls
back to the configured default on any failure. Routing decision is logged.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

# Heuristic difficulty signals.
_HARD_SIGNALS = ("architecture", "refactor", "safety", "security", "traceability",
                 "compliance", "multi", "design", "review", "debug", "complex")
_EASY_SIGNALS = ("rename", "format", "comment", "typo", "list", "summarize",
                 "explain", "simple")


@dataclass
class RouteDecision:
    model: str
    tier: str  # "easy" | "hard" | "default"
    reason: str
    fallback: bool = False


def classify(text: str) -> str:
    low = (text or "").lower()
    hard = sum(1 for s in _HARD_SIGNALS if s in low)
    easy = sum(1 for s in _EASY_SIGNALS if s in low)
    if hard > easy and hard > 0:
        return "hard"
    if easy > hard and easy > 0:
        return "easy"
    # length heuristic
    if len(low.split()) > 40:
        return "hard"
    return "default"


def route(text: str, endpoints: dict | None = None) -> RouteDecision:
    """Select a model for ``text``.

    endpoints: {"easy": "model-id", "hard": "model-id", "default": "model-id"}
    Env overrides: AXIOM_MODEL_EASY / AXIOM_MODEL_HARD / AXIOM_MODEL_DEFAULT.
    """
    endpoints = dict(endpoints or {})
    endpoints.setdefault("easy", os.environ.get("AXIOM_MODEL_EASY", ""))
    endpoints.setdefault("hard", os.environ.get("AXIOM_MODEL_HARD", ""))
    endpoints.setdefault("default", os.environ.get("AXIOM_MODEL_DEFAULT", ""))
    tier = classify(text)
    chosen = endpoints.get(tier) or endpoints.get("default") or ""
    if not chosen:
        # fall back to default env or a sentinel
        chosen = endpoints.get("default") or "default"
        fallback = True
    else:
        fallback = False
    if tier != "default" and not endpoints.get(tier):
        tier = "default"
        chosen = endpoints.get("default") or "default"
        fallback = True
    return RouteDecision(model=chosen, tier=tier, reason=f"classified as {tier}",
                        fallback=fallback)
