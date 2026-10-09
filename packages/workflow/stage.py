"""Evidence-based project-stage detection (heuristic).

The declared lifecycle stage lives in a profile (`entry:` mapped to a phase
via packages/workflow/entry.py). This module answers the complementary
question: given a project directory, what is the deepest V-Model phase with
real artifact evidence on disk?

Heuristic only: directory/file markers imply a phase has been worked, never
that it is complete or approved. On conflict, the declared profile entry
wins; callers should surface both.
"""

from __future__ import annotations

import pathlib

# V-Model phase order used by packages/workflow/entry.py values.
V_MODEL_ORDER = [
    "concept",
    "system-architecture",
    "detailed-design",
    "unit-verification",
    "verification",
    "maintenance",
]

# Phase -> root-level marker names (directory or file, case-insensitive).
# A marker means the phase has produced evidence, so the project has
# reached *at least* that phase.
STAGE_MARKERS: dict[str, tuple[str, ...]] = {
    "concept": ("requirements", "requirements.md", "stakeholders"),
    "system-architecture": ("architecture", "architecture.md", "icd"),
    "detailed-design": ("design", "headers", "src"),
    "unit-verification": ("tests", "test", "test-results"),
    "verification": ("evidence", "validation", "hil", "vehicle"),
    "maintenance": ("changelog.md", "change-log", "releases"),
}


def detect_stage(root: str | pathlib.Path) -> dict:
    """Detect the deepest evidenced V-Model phase under root.

    Returns {"stage", "phase_index", "evidence": {phase: [markers found]}}.
    "stage" is None when no marker matches (greenfield / empty checkout).
    """
    base = pathlib.Path(root)
    present = set()
    if base.is_dir():
        for child in base.iterdir():
            present.add(child.name.lower())
    evidence: dict[str, list[str]] = {}
    deepest: str | None = None
    for phase in V_MODEL_ORDER:
        found = sorted(m for m in STAGE_MARKERS[phase] if m in present)
        if found:
            evidence[phase] = found
            deepest = phase
    return {
        "stage": deepest,
        "phase_index": V_MODEL_ORDER.index(deepest) if deepest else -1,
        "evidence": evidence,
    }


def reconcile_stage(
    detected: str | None, declared_phase: str | None
) -> dict:
    """Combine detected (evidence) and declared (profile entry) stages.

    Rule: explicit declaration wins on conflict; detection is advisory.
    "next_phase" is the phase after whichever stage is recommended.
    """
    recommended = declared_phase or detected
    conflict = bool(detected and declared_phase and detected != declared_phase)
    try:
        nxt: str | None = V_MODEL_ORDER[V_MODEL_ORDER.index(recommended) + 1]
    except (ValueError, IndexError, TypeError):
        nxt = None
    return {
        "detected_stage": detected,
        "declared_stage": declared_phase,
        "recommended_stage": recommended,
        "conflict": conflict,
        "next_phase": nxt,
    }
