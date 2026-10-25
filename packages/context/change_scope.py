from __future__ import annotations
from pathlib import Path
import subprocess

def git_changed_files(root: str | Path) -> list[str]:
    """Files changed vs HEAD (staged + unstaged + untracked), de-duplicated."""
    out: list[str] = []
    seen: set[str] = set()
    cmds = (
        ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACMRT", "HEAD"],
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
    )
    for cmd in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                out.append(line)
    return out
