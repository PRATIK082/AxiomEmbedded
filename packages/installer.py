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
import subprocess
import sys

CLIENTS = ("opencode", "claude", "codex", "gemini", "copilot",
           "cursor", "cline", "aider", "kilo", "openhands")

# Clients sharing an install path (documented, not duplicated):
# - GitHub Copilot Coding Agent / Agent Mode reuse the "copilot" branch
#   (.github/copilot-instructions.md + .vscode/mcp.json entry).
# - Claude Code IS the "claude" branch (.mcp.json + .claude/skills/).


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


def ensure_generated(source: pathlib.Path) -> str | None:
    """Generate client mirrors into source when absent.

    Mirrors under .opencode/.claude are gitignored build outputs; a fresh
    clone has sources (skills/, agents/) but no mirrors. Install/update/
    uninstall read the mirrors as their file source, so generate them on
    demand here instead of silently shipping nothing. Returns a note when
    generation ran, else None.
    """
    markers = (source / ".opencode" / "skills", source / ".claude" / "skills")
    if all(m.is_dir() and any(m.iterdir()) for m in markers):
        return None
    script = source / "scripts" / "sync_clients.py"
    if not script.exists():
        return ("client mirrors absent and no generator found: "
                "agents/skills not installed")
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(source)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"sync_clients.py failed: {(proc.stdout + proc.stderr)[-2000:]}")
    return "client mirrors were absent: generated on demand (gitignored build output)"


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


def _filter_skill_relpaths(source: pathlib.Path, rels: list[str],
                           domains: list[str] | None,
                           groups: list[str] | None = None) -> tuple[list[str], str]:
    """Keep only skills matching selected domains/groups.

    Skill binding is DATA (SKILL.md frontmatter + groups.yaml ->
    skill-index.json), so no .py change is ever needed when skills gain or
    change domains or groups: the index built by `axiom skills apply`
    drives this filter automatically. Domains and groups combine with AND.
    """
    if not domains and not groups:
        return rels, ""
    try:
        idx = json.loads((source / "registries" / "skill-index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return rels, "skill index unreadable: domain/group filter skipped"
    if groups:
        known = set(idx.get("by_group", {}))
        unknown = sorted(set(groups) - known)
        if unknown:
            raise ValueError(f"unknown skill group(s): {', '.join(unknown)} "
                             f"(known: {', '.join(sorted(known))})")
        in_groups = {sid for g in groups for sid in idx["by_group"].get(g, [])}
    else:
        in_groups = None
    want = set(domains or [])
    keep: list[str] = []
    for rel in rels:
        parts = pathlib.PurePosixPath(rel).parts
        if len(parts) < 3 or parts[1] != "skills":
            keep.append(rel)  # agents/commands/plugins: not domain-scoped
            continue
        sid = parts[2]
        if in_groups is not None and sid not in in_groups:
            continue
        entry = idx.get("skills", {}).get(sid, {})
        entry_domains = set(entry.get("domains", []))
        if want and "all" not in entry_domains and not (entry_domains & want):
            continue
        keep.append(rel)
    scope = "+".join(filter(None, [
        f"domains={sorted(want)}" if want else "",
        f"groups={sorted(groups)}" if groups else ""]))
    return keep, f"filter {scope}: {len(keep)}/{len(rels)} files"


def install_client(client: str, dest: pathlib.Path, home: pathlib.Path,
                   source: pathlib.Path | None, *, is_global: bool,
                   domains: list[str] | None = None,
                   groups: list[str] | None = None) -> dict:
    if client not in CLIENTS:
        raise ValueError(f"unknown client: {client} (choose from {', '.join(CLIENTS)})")
    server, server_note = mcp_command()
    written, merged, skipped, notes = [], [], [], [server_note]
    if source is None:
        notes.append("no axiom content source found: MCP registration only (use --source DIR for agents/skills)")
    else:
        note = ensure_generated(source)
        if note:
            notes.append(note)

    if client == "opencode":
        root = home / ".config" / "opencode" if is_global else dest
        server, server_note = opencode_mcp_entry()
        notes[0] = server_note
        if source is not None:
            rels = (_generated_relpaths(source, ".opencode", "agents")
                    + _generated_relpaths(source, ".opencode", "skills")
                    + _generated_relpaths(source, ".opencode", "commands")
                    + _generated_relpaths(source, ".opencode", "plugins"))
            rels, note = _filter_skill_relpaths(source, rels, domains, groups)
            if note:
                notes.append(note)
            w, s = _copy_generated(source, root, rels)
            written += w
            skipped += s
        if (not is_global and source is not None
                and pathlib.Path(dest).resolve() == source.resolve()):
            # Installing into the Axiom checkout itself must not re-add the
            # self-referencing MCP server (scripts/sync_clients.py removes it
            # from this checkout's opencode.json on purpose).
            notes.append("self-install skipped: this checkout must not load its own "
                         "axiom-embedded MCP server (see scripts/sync_clients.py)")
        else:
            merged.append(f"opencode.json#{_merge_json(root / 'opencode.json', ['mcp', 'axiom-embedded'], server)}")

    elif client == "claude":
        root = home / ".claude" if is_global else dest
        if source is not None:
            rels = _generated_relpaths(source, ".claude", "agents") + _generated_relpaths(source, ".claude", "skills")
            rels, note = _filter_skill_relpaths(source, rels, domains, groups)
            if note:
                notes.append(note)
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
            notes.append("same files serve GitHub Copilot Coding Agent / Agent Mode (repo-scoped instructions + MCP)")

    elif client == "cursor":
        cfg = home / ".cursor" / "mcp.json" if is_global else dest / ".cursor" / "mcp.json"
        merged.append(f"{cfg}#{_merge_json(cfg, ['mcpServers', 'axiom-embedded'], server)}")
        notes.append("Cursor discovers skills at runtime via the axiom MCP server (search_skills/engage); no skill files to copy")

    elif client == "cline":
        root = home / ".cline" if is_global else dest
        cfg = root / "mcp.json" if is_global else dest / ".cline" / "mcp.json"
        merged.append(f"{cfg}#{_merge_json(cfg, ['mcpServers', 'axiom-embedded'], server)}")
        notes.append("Cline discovers skills at runtime via the axiom MCP server; no skill files to copy")

    elif client == "openhands":
        # OpenHands reads the user-global config even for project work.
        cfg = home / ".openhands" / "mcp.json"
        merged.append(f"{cfg}#{_merge_json(cfg, ['mcpServers', 'axiom-embedded'], server)}")
        if not is_global:
            notes.append("OpenHands reads the user-global ~/.openhands/mcp.json even for project work; merged there")
        notes.append("OpenHands discovers skills at runtime via the axiom MCP server; no skill files to copy")

    elif client == "aider":
        import yaml as _yaml
        cfg = (home if is_global else dest) / ".aider.conf.yml"
        if cfg.exists():
            skipped.append(".aider.conf.yml")
            notes.append("existing .aider.conf.yml kept: add an mcp-servers entry pointing at `axiom mcp` (see clients/MCP_CLIENTS.md)")
        else:
            cfg.write_text(_yaml.safe_dump({"mcp-servers": {
                "axiom-embedded": {"command": server["command"], "args": server["args"]}}},
                sort_keys=False), encoding="utf-8")
            written.append(".aider.conf.yml")
        notes.append("Aider discovers skills at runtime via the axiom MCP server; no skill files to copy")

    elif client == "kilo":
        cfg = home / ".config" / "kilo" / "kilo.jsonc" if is_global else dest / ".kilo" / "kilo.jsonc"
        if cfg.exists():
            skipped.append(".kilo/kilo.jsonc")
            notes.append("existing .kilo/kilo.jsonc kept (JSONC comments are not machine-mergeable): add an mcp entry pointing at `axiom mcp` (see clients/MCP_CLIENTS.md)")
        else:
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(json.dumps({"mcp": {"axiom-embedded": {
                "command": server["command"], "args": server["args"]}}}, indent=2) + "\n", encoding="utf-8")
            written.append(".kilo/kilo.jsonc")
        notes.append("Kilo Code discovers skills at runtime via the axiom MCP server; no skill files to copy")

    return {"client": client, "scope": "global" if is_global else "project",
            "dest": str(dest if not is_global else home),
            "domains": sorted(domains) if domains else "all",
            "groups": sorted(groups) if groups else "all",
            "written": written, "merged": merged, "skipped": skipped, "notes": notes}


def _unmerge_json(path: pathlib.Path, key_path: list[str]) -> str:
    """Remove a merged key; unlinks the file if it becomes empty. Never touches other keys."""
    if not path.exists():
        return "absent"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return "unparseable-kept"
    node = data
    for key in key_path[:-1]:
        if not isinstance(node.get(key), dict):
            return "absent"
        node = node[key]
    if key_path[-1] not in node:
        return "absent"
    del node[key_path[-1]]
    if data == {}:
        path.unlink()
        return "removed-empty-file"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return "removed"


def _unmerge_toml_section(path: pathlib.Path, header: str) -> str:
    """Drop one [section] block; keeps every other line byte-identical."""
    if not path.exists():
        return "absent"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out, skipped, in_block = [], False, False
    for ln in lines:
        if ln.strip() == header:
            in_block = True
            skipped = True
            continue
        if in_block and ln.lstrip().startswith("["):
            in_block = False
        if not in_block:
            out.append(ln)
    if not skipped:
        return "absent"
    if not "".join(out).strip():
        path.unlink()
        return "removed-empty-file"
    path.write_text("".join(out), encoding="utf-8")
    return "removed"


def _delete_if_pristine(src: pathlib.Path, dst: pathlib.Path) -> str:
    """Delete dst only when its bytes still match src (never user content)."""
    if not dst.exists():
        return "absent"
    if src.exists() and dst.read_bytes() == src.read_bytes():
        dst.unlink()
        return "removed"
    return "kept-divergent"


def _client_file_map(client: str, dest: pathlib.Path, home: pathlib.Path,
                     source: pathlib.Path | None, *, is_global: bool,
                     domains: list[str] | None = None,
                     groups: list[str] | None = None):
    """Return (copied: [(src, dst)], configs: [(path, kind, key)]) for uninstall/update.

    copied: generated files safe to delete/refresh only on byte-match.
    configs: (path, 'json'|'toml', key_path|header) merge points.
    """
    copied: list[tuple[pathlib.Path, pathlib.Path]] = []
    configs: list[tuple[pathlib.Path, str, object]] = []
    if source is not None:
        ensure_generated(source)

    def _copy_rels(prefix: str, kind: str, root: pathlib.Path):
        if source is None:
            return
        rels = _generated_relpaths(source, prefix, kind)
        if kind == "skills":
            rels, _ = _filter_skill_relpaths(source, rels, domains, groups)
        for rel in rels:
            copied.append((source / rel, root / rel))

    if client == "opencode":
        root = home / ".config" / "opencode" if is_global else dest
        _copy_rels(".opencode", "agents", root)
        _copy_rels(".opencode", "skills", root)
        _copy_rels(".opencode", "commands", root)
        _copy_rels(".opencode", "plugins", root)
        configs.append((root / "opencode.json", "json", ["mcp", "axiom-embedded"]))
    elif client == "claude":
        root = home / ".claude" if is_global else dest
        _copy_rels(".claude", "agents", root)
        _copy_rels(".claude", "skills", root)
        if is_global:
            configs.append((home / ".claude.json", "json", ["mcpServers", "axiom-embedded"]))
        else:
            configs.append((root / ".mcp.json", "json", ["mcpServers", "axiom-embedded"]))
    elif client == "codex":
        cfg = home / ".codex" / "config.toml" if is_global else dest / ".codex" / "config.toml"
        configs.append((cfg, "toml", "[mcp_servers.axiom-embedded]"))
    elif client == "gemini":
        cfg = home / ".gemini" / "settings.json" if is_global else dest / ".gemini" / "settings.json"
        configs.append((cfg, "json", ["mcpServers", "axiom-embedded"]))
        target = root_gemini_md(home) if is_global else dest / "GEMINI.md"
        if source is not None:
            copied.append((source / "GEMINI.md", target))
    elif client == "copilot":
        if not is_global and source is not None:
            copied.append((source / ".github" / "copilot-instructions.md",
                            dest / ".github" / "copilot-instructions.md"))
    elif client == "cursor":
        cfg = home / ".cursor" / "mcp.json" if is_global else dest / ".cursor" / "mcp.json"
        configs.append((cfg, "json", ["mcpServers", "axiom-embedded"]))
    elif client == "cline":
        root = home / ".cline" if is_global else dest
        cfg = root / "mcp.json" if is_global else dest / ".cline" / "mcp.json"
        configs.append((cfg, "json", ["mcpServers", "axiom-embedded"]))
    elif client == "openhands":
        configs.append((home / ".openhands" / "mcp.json", "json", ["mcpServers", "axiom-embedded"]))
    elif client == "aider":
        pass  # YAML content compared separately (comment-preserving)
    elif client == "kilo":
        pass  # JSONC compared separately (comment-preserving)
    return copied, configs


def uninstall_client(client: str, dest: pathlib.Path, home: pathlib.Path,
                     source: pathlib.Path | None = None, *, is_global: bool) -> dict:
    """Remove everything install_client wrote. Merge entries are unmerged
    (other user content untouched); copied files are deleted only when their
    bytes still match the source (divergent = user-owned = kept + reported)."""
    if client not in CLIENTS:
        raise ValueError(f"unknown client: {client} (choose from {', '.join(CLIENTS)})")
    removed, kept, notes = [], [], []
    copied, configs = _client_file_map(client, dest, home, source, is_global=is_global)
    for path, kind, key in configs:
        if kind == "json":
            stent = _unmerge_json(path, key)  # type: ignore[arg-type]
        else:
            stent = _unmerge_toml_section(path, key)  # type: ignore[arg-type]
        (removed if stent.startswith("removed") or stent == "absent" else kept).append(f"{path}#{stent}")
    for src, dst in copied:
        stent = _delete_if_pristine(src, dst)
        (removed if stent in ("removed", "absent") else kept).append(f"{dst}#{stent}")
    if client == "aider":
        kept, removed = _uninstall_hand_managed(
            (home if is_global else dest) / ".aider.conf.yml", _expected_aider_yml(), kept, removed, notes,
            "add an mcp-servers entry pointing at `axiom mcp` to re-install")
    elif client == "kilo":
        kept, removed = _uninstall_hand_managed(
            (home / ".config" / "kilo" / "kilo.jsonc") if is_global else (dest / ".kilo" / "kilo.jsonc"),
            _expected_kilo_jsonc(), kept, removed, notes,
            "add an mcp entry pointing at `axiom mcp` to re-install")
    elif client == "copilot":
        notes.append("remove .vscode/mcp.json entry manually if you added one (see clients/COPILOT.md)")
    return {"client": client, "scope": "global" if is_global else "project",
            "action": "uninstall", "removed": removed, "kept": kept, "notes": notes}


def _expected_aider_yml() -> str:
    import yaml as _yaml
    server, _ = mcp_command()
    return _yaml.safe_dump({"mcp-servers": {
        "axiom-embedded": {"command": server["command"], "args": server["args"]}}},
        sort_keys=False)


def _expected_kilo_jsonc() -> str:
    server, _ = mcp_command()
    return json.dumps({"mcp": {"axiom-embedded": {
        "command": server["command"], "args": server["args"]}}}, indent=2) + "\n"


def _uninstall_hand_managed(path: pathlib.Path, expected: str, kept: list[str],
                             removed: list[str], notes: list[str], reinstall_hint: str):
    if not path.exists():
        removed.append(f"{path}#absent")
    elif path.read_text(encoding="utf-8") == expected:
        path.unlink()
        removed.append(f"{path}#removed")
    else:
        kept.append(f"{path}#kept-divergent")
        notes.append(f"{path} was hand-edited; kept. {reinstall_hint} (see clients/MCP_CLIENTS.md)")
    return kept, removed


def update_client(client: str, dest: pathlib.Path, home: pathlib.Path,
                  source: pathlib.Path | None, *, is_global: bool,
                  domains: list[str] | None = None,
                  groups: list[str] | None = None, force: bool = False) -> dict:
    """Refresh an install: re-run install (copies missing files, merges
    config), then refresh stale copies. Without force, divergent files are
    reported, not overwritten; with force they are refreshed from source."""
    res = install_client(client, dest, home, source, is_global=is_global, domains=domains,
                         groups=groups)
    refreshed, stale = [], []
    copied, _ = _client_file_map(client, dest, home, source, is_global=is_global, domains=domains,
                                 groups=groups)
    for src, dst in copied:
        if not dst.exists() or not src.exists():
            continue
        if dst.read_bytes() != src.read_bytes():
            if force:
                dst.write_bytes(src.read_bytes())
                refreshed.append(str(dst))
            else:
                stale.append(str(dst))
    res["action"] = "update"
    res["refreshed"] = refreshed
    res["stale"] = stale
    if stale and not force:
        res["notes"] = [*res.get("notes", []),
                        f"{len(stale)} file(s) differ from source; re-run with force to refresh (divergent content kept by default)"]
    return res


def root_gemini_md(home: pathlib.Path) -> pathlib.Path:
    return home / ".gemini" / "GEMINI.md"
