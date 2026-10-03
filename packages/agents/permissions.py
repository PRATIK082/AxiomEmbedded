SAFE_DEFAULTS = {
    "read": "allow",
    "edit": "ask",
    "bash": "ask",
    "external_directory": "deny",
    "git_push": "ask",
    "release": "ask",
}

def can(action: str, requested: str) -> bool:
    policy = SAFE_DEFAULTS.get(action, "ask")
    return policy == "allow" or (policy == "ask" and requested == "approved")
