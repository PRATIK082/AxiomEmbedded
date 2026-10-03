ENTRY = {
    "greenfield": "concept",
    "requirements_available": "system-architecture",
    "architecture_available": "detailed-design",
    "implementation_available": "unit-verification",
    "verification_in_progress": "verification",
    "maintenance": "maintenance",
    "incident_recovery": "defect-analysis",
    "brownfield": "discovery",
}

def starting_phase(entry_mode: str) -> str:
    return ENTRY.get(entry_mode, "unknown")
