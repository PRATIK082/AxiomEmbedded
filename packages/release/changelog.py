"""Changelog / release notes generation from git history."""
from __future__ import annotations

import subprocess
from pathlib import Path


def git_log(repo: str | Path, since_tag: str | None = None, limit: int = 100) -> list[dict]:
    cwd = Path(repo).resolve()
    cmd = ["git", "-C", str(cwd), "log", f"-{limit}", "--pretty=format:%H|%s|%an|%ad", "--date=short"]
    if since_tag:
        cmd.append(f"{since_tag}..HEAD")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return []
    commits = []
    for line in out.splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commits.append({"hash": parts[0][:8], "subject": parts[1],
                        "author": parts[2], "date": parts[3]})
    return commits


def generate_changelog(repo: str | Path, since_tag: str | None = None,
                       version: str | None = None) -> str:
    commits = git_log(repo, since_tag)
    lines = []
    if version:
        lines.append(f"# Release {version}")
        lines.append("")
    # group by conventional-commit prefix
    groups: dict[str, list[str]] = {}
    for c in commits:
        subj = c["subject"]
        prefix = subj.split(":", 1)[0].lower() if ":" in subj else "other"
        if prefix not in ("feat", "fix", "docs", "chore", "refactor", "test", "perf"):
            prefix = "other"
        groups.setdefault(prefix, []).append(f"- {subj} ({c['hash']})")
    for g in ("feat", "fix", "docs", "refactor", "perf", "test", "chore", "other"):
        if g in groups:
            lines.append(f"## {g}")
            lines.extend(groups[g])
            lines.append("")
    return "\n".join(lines).strip() + "\n"
