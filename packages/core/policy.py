from dataclasses import dataclass

@dataclass(frozen=True)
class PermissionPolicy:
    filesystem: str = "read-only"
    network: str = "disabled"
    git_write: bool = False
    require_human_approval: bool = True

    def allows(self, action: str) -> bool:
        if action in {"commit", "push", "merge", "release", "production-write"}:
            return self.git_write and not self.require_human_approval
        return True
