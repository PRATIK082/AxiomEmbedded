# SPDX-License-Identifier: Apache-2.0
"""Install the Axiom pack into a project (or user-global config) per client.

Single implementation behind `axiom install --client ...`. Rules:

- Merge into existing config files; never clobber user content.
- Copy generated agent/skill files from the axiom content source
  (source checkout by default; ``--source`` override). When no content
  source is available (bare wheel install), register the MCP server only
  and say so honestly.
- Prefer the ``axiom`` shim on PATH; fall back to ``python -m axiom_cli``.
"""

from __future__ import annotations

import json
import pathlib
import shutil

CLIENTS = ("opencode", "claude", "codex", "gemini", "copilot")


def find_content_source(explicit: str | pathlib.Path | None = None) -> pathlib.Path | None:
    if explicit is not None:
        candidate = pathlib.Path(explicit)
        if (candidate / "skills").is_dir() and (candidate / "agents").is_dir():
            return candidate
        raise ValueError(f"content source has no skills/ and agents/: {candidate}")
    here = pathlib.Path(__file__).resolve()
    for parent in [here.parents[1]] + list(here.parents):
        if (parent / "skills").is_dir() and (parent / "agents").is_dir():
            return parent
    return None


def mcp_command() -> tuple[dict, str]:
    """Return (server_entry, note) for this machine."""
    if shutil.which("axiom"):
        return (
            {"command": "axiom", "args": ["mcp"],
             "description": "AxiomEmbedded skills, plans, context, impact, workflow tools"},
            "using `axiom` shim from PATH",
        )
    return (
        {"command": "python", "args": ["-m", "axiom_cli", "mcp"],
         "description": "AxiomEmbedded skills, plans, context, impact, workflow tools"},
        "no `axiom` shim on PATH (`pipx install axiom-embedded` recommended); using `python -m axiom_cli mcp`",
    )


def opencode_mcp_entry() -> tuple[dict, str]:
    """OpenCode-shaped entry: strict `{type: local, command: [...], enabled}`.

    OpenCode v1 rejects the generic `{command, args}` split (verified via
    `opencode mcp list`), so the opencode installer branch uses this.
    """
    server, note = mcp_command()
    return ({"type": "local", "command": [server["command"], *server["args"]],
             "enabled": True}, note)


def _merge_json(path: pathlib.Path, key_path: list[str], value: dict) -> str:
    """Merge value at nested key_path; returns 'merged'|'present'."""
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    node = data
    for key in key_path[:-1]:
        node = node.setdefault(key, {})
    if node.get(key_path[-1]) == value:
        return "present"
    node[key_path[-1]] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return "merged"


def _append_toml_section(path: pathlib.Path, header: str, body: str) -> str:
    if path.exists() and header in path.read_text(encoding="utf-8"):
        return "present"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        if path.stat().st_size:
            fh.write("\n")
        fh.write(f"{header}\n{body}\n")
    return "merged"


def _copy_generated(source: pathlib.Path, dest: pathlib.Path, relpaths: list[str]) -> tuple[list[str], list[str]]:
    written, skipped = [], []
    for rel in relpaths:
        src, dst = source / rel, dest / rel
        if not src.exists():
            continue
        if dst.exists():
            if dst.read_text(encoding="utf-8") != src.read_text(encoding="utf-8"):
                skipped.append(rel)  # divergent user content: never clobber
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        written.append(rel)
    return written, skipped


def _generated_relpaths(source: pathlib.Path, prefix: str, kind: str) -> list[str]:
    """Agent/skill/command/plugin paths under .opencode or .claude in the axiom tree."""
    base = source / prefix / kind
    if not base.is_dir():
        return []
    if kind == "agents":
        return [f"{prefix}/agents/{p.name}" for p in sorted(base.iterdir()) if p.suffix == ".md"]
    if kind == "commands":
        return [f"{prefix}/commands/{p.name}" for p in sorted(base.iterdir()) if p.suffix == ".md"]
    if kind == "plugins":
        return [f"{prefix}/plugins/{p.name}" for p in sorted(base.iterdir())
                if p.suffix in (".ts", ".js")]
    out = []
    for skill_dir in sorted(base.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_dir.is_dir() and skill_md.exists():
            out.append(f"{prefix}/skills/{skill_dir.name}/SKILL.md")
    return out


def install_client(client: str, dest: pathlib.Path, home: pathlib.Path,
                   source: pathlib.Path | None, *, is_global: bool) -> dict:
    if client not in CLIENTS:
        raise ValueError(f"unknown client: {client} (choose from {', '.join(CLIENTS)})")
    server, server_note = mcp_command()
    written, merged, skipped, notes = [], [], [], [server_note]
    if source is None:
        notes.append("no axiom content source found: MCP registration only (use --source DIR for agents/skills)")

    if client == "opencode":
        root = home / ".config" / "opencode" if is_global else dest
        server, server_note = opencode_mcp_entry()
        notes[0] = server_note
        if source is not None:
            rels = (_generated_relpaths(source, ".opencode", "agents")
                    + _generated_relpaths(source, ".opencode", "skills")
                    + _generated_relpaths(source, ".opencode", "commands")
                    + _generated_relpaths(source, ".opencode", "plugins"))
            w, s = _copy_generated(source, root, rels)
            written += w
            skipped += s
        merged.append(f"opencode.json#{_merge_json(root / 'opencode.json', ['mcp', 'axiom-embedded'], server)}")

    elif client == "claude":
        root = home / ".claude" if is_global else dest
        if source is not None:
            rels = _generated_relpaths(source, ".claude", "agents") + _generated_relpaths(source, ".claude", "skills")
            w, s = _copy_generated(source, root, rels)
            written += w
            skipped += s
        if is_global:
            merged.append(f"~/.claude.json#{_merge_json(home / '.claude.json', ['mcpServers', 'axiom-embedded'], server)}")
        else:
            merged.append(f".mcp.json#{_merge_json(root / '.mcp.json', ['mcpServers', 'axiom-embedded'], server)}")

    elif client == "codex":
        cfg = home / ".codex" / "config.toml" if is_global else dest / ".codex" / "config.toml"
        body = f"command = {json.dumps(server['command'])}\nargs = {json.dumps(server['args'])}"
        merged.append(f"{cfg}#{_append_toml_section(cfg, '[mcp_servers.axiom-embedded]', body)}")
        notes.append("Codex reads AGENTS.md automatically; no instruction files to copy")

    elif client == "gemini":
        cfg = home / ".gemini" / "settings.json" if is_global else dest / ".gemini" / "settings.json"
        merged.append(f"{cfg}#{_merge_json(cfg, ['mcpServers', 'axiom-embedded'], server)}")
        if source is not None:
            target = root_gemini_md(home) if is_global else dest / "GEMINI.md"
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((source / "GEMINI.md").read_text(encoding="utf-8"), encoding="utf-8")
                written.append(str(target))
            else:
                skipped.append(str(target))

    elif client == "copilot":
        if is_global:
            notes.append("Copilot has no global instruction file: configure the MCP server in your editor (.vscode/mcp.json, entry in clients/mcp.json) and keep instructions per repository")
        else:
            if source is not None:
                target = dest / ".github" / "copilot-instructions.md"
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text((source / ".github" / "copilot-instructions.md").read_text(encoding="utf-8"), encoding="utf-8")
                    written.append(".github/copilot-instructions.md")
                else:
                    skipped.append(".github/copilot-instructions.md")
            notes.append("for MCP in VS Code, copy clients/mcp.json to .vscode/mcp.json (see clients/COPILOT.md)")

    return {"client": client, "scope": "global" if is_global else "project",
            "dest": str(dest if not is_global else home),
            "written": written, "merged": merged, "skipped": skipped, "notes": notes}


def root_gemini_md(home: pathlib.Path) -> pathlib.Path:
    return home / ".gemini" / "GEMINI.md"
