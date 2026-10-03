from __future__ import annotations

INTENT_MAP = {
    "bug": "debugging",
    "defect": "debugging",
    "feature": "implementation",
    "review": "code-review",
    "test": "test-engineering",
    "architecture": "software-architecture",
    "requirement": "requirements",
    "audit": "project-audit",
    "brownfield": "brownfield-recovery",
}

def route(text: str) -> str:
    lower = text.lower()
    for key, agent in INTENT_MAP.items():
        if key in lower:
            return agent
    return "engineering-manager"
