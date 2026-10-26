from dataclasses import dataclass

@dataclass(frozen=True)
class PermissionPolicy:
    filesystem: str = "read-only"
    network: str = "disabled"
    git_write: bool = False
    require_human_approval: bool = True

    # Known-safe read-only actions that never require approval.
    _SAFE_ACTIONS = {"read", "analyze", "plan", "select", "inspect"}

    def allows(self, action: str) -> bool:
        if action in self._SAFE_ACTIONS:
            return True
        if action in {"commit", "push", "merge", "release", "production-write"}:
            return self.git_write and not self.require_human_approval
        # Default-deny: unknown/sensitive actions require explicit approval.
        return False
