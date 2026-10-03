from __future__ import annotations
from pathlib import Path
import subprocess

def git_changed_files(root: str | Path) -> list[str]:
    try:
        result = subprocess.run(["git","-C",str(root),"diff","--name-only","--diff-filter=ACMRT"], capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
