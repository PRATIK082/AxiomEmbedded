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


# Prompt -> domain detection. Distinctive, low-collision keywords only:
# generic English words ("can", "cal", "body", "code") are excluded on
# purpose. Sources: the 11 automotive skills' descriptions in
# registries/skill-index.json. First match wins; None = no signal.
DOMAIN_KEYWORDS = {
    "automotive": [
        "automotive", "asil", "hara", "sotif", "fusa", "v-model",
        "uds", "misra", "autosar", "aspice", "oem", "ecu", "obd",
        "doip", "adas", "ncap", "secoc", "flexray", "j1939",
        "some/ip", "canfd", "can-fd", "can-xl", "lin bus", "v2x",
        "tara", "qnx", "aaos", "aeb", "bcm", "peps",
        "21434", "26262", "21448", "r155", "r156",
    ],
}


def detect_domain(text: str) -> str | None:
    """Return the best-guess domain for a free-text prompt, or None."""
    lower = text.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for key in keywords:
            if key in lower:
                return domain
    return None
